"""Matching Engine for Organ Donation Platform"""
import os
import pickle
from datetime import datetime, timezone
from database import (
    DatabaseManager, Donor, Match, SOSCase, BloodGroup, OrganType,
    get_blood_compatible_groups, ApprovalStatus
)
from sqlalchemy import and_, or_

class MatchingEngine:
    def __init__(self, db_manager=None, model_path="data/match_model.pkl"):
        self.db_manager = db_manager or DatabaseManager()
        self.model_path = model_path
        self.ml_model = None
        self.load_model()
    
    def load_model(self):
        """Load trained ML model if available"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.ml_model = pickle.load(f)
                print("✅ ML model loaded successfully")
            except Exception as e:
                print(f"⚠️ Could not load ML model: {str(e)}")
                self.ml_model = None
        else:
            print("⚠️ ML model not found. Using rule-based matching only.")
    
    def find_matches(self, sos_case_id=None, patient_data=None, max_results=20, search_radius_km=500):
        """
        Find matching donors based on SOS case or patient data
        
        Args:
            sos_case_id: ID of existing SOS case
            patient_data: Dict with patient info if not using SOS case
            max_results: Maximum number of matches to return
            search_radius_km: Maximum search radius
        
        Returns:
            List of match objects with scores
        """
        session = self.db_manager.get_session()
        
        try:
            # Get patient information
            if sos_case_id:
                sos_case = session.query(SOSCase).filter_by(id=sos_case_id).first()
                if not sos_case:
                    return []
                
                patient_blood_group = sos_case.blood_group
                organ_required = sos_case.organ_required
                urgency_level = sos_case.urgency_level
                patient_age = sos_case.patient_age
                patient_city = sos_case.city
                patient_state = sos_case.state
            elif patient_data:
                patient_blood_group = patient_data.get('blood_group')
                organ_required = patient_data.get('organ_type')
                urgency_level = patient_data.get('urgency_level', 3)
                patient_age = patient_data.get('age')
                patient_city = patient_data.get('city')
                patient_state = patient_data.get('state')
            else:
                return []
            
            # Step 1: Rule-based filtering
            compatible_blood_groups = get_blood_compatible_groups(patient_blood_group)
            
            # Query available donors
            donors_query = session.query(Donor).filter(
                and_(
                    Donor.organ_type == organ_required,
                    Donor.availability_status == True,
                    Donor.approval_status == ApprovalStatus.APPROVED,
                    Donor.blood_group.in_(compatible_blood_groups)
                )
            )
            
            donors = donors_query.all()
            
            if not donors:
                return []
            
            # Step 2: Calculate features and scores for each donor
            matches = []
            for donor in donors:
                # Blood compatibility
                blood_compatible = donor.blood_group in compatible_blood_groups
                
                # Organ match (already filtered)
                organ_match = donor.organ_type == organ_required
                
                # Age compatibility (within 20 years for most organs)
                age_diff = abs(donor.age - patient_age)
                age_compatible = age_diff <= 20
                
                # Location matching and distance
                distance_km = None
                location_score = 0.5
                
                # Simple city/state matching
                if donor.city and patient_city:
                    if donor.city.lower() == patient_city.lower():
                        location_score = 1.0
                        distance_km = 0
                    elif donor.state and patient_state and donor.state.lower() == patient_state.lower():
                        location_score = 0.7
                        distance_km = 100  # Approximate
                    else:
                        location_score = 0.3
                        distance_km = 300  # Approximate
                
                # Skip if too far
                if distance_km and distance_km > search_radius_km:
                    continue
                
                # Compatibility score (0-1)
                compatibility_score = (
                    (1.0 if blood_compatible else 0.0) * 0.4 +
                    (1.0 if organ_match else 0.0) * 0.3 +
                    (1.0 if age_compatible else 0.5) * 0.2 +
                    location_score * 0.1
                )
                
                # Urgency weight (1-5 scale)
                urgency_weight = urgency_level / 5.0
                
                # Donor reliability score
                reliability = donor.reliability_score or 0.5
                
                # Calculate listing freshness (days since registration)
                days_since_registration = (datetime.now(timezone.utc) - donor.registration_date).days
                freshness_score = max(0.5, 1.0 - (days_since_registration / 365))
                
                # Feature vector for ML model
                features = {
                    'blood_compatible': 1.0 if blood_compatible else 0.0,
                    'organ_match': 1.0 if organ_match else 0.0,
                    'age_compatible': 1.0 if age_compatible else 0.0,
                    'distance_normalized': min(1.0, (distance_km or 100) / search_radius_km) if distance_km else 0.5,
                    'urgency_weight': urgency_weight,
                    'reliability_score': reliability,
                    'freshness_score': freshness_score,
                    'compatibility_score': compatibility_score
                }
                
                # ML prediction (if model available)
                match_probability = 0.5
                if self.ml_model:
                    try:
                        feature_vector = [
                            features['blood_compatible'],
                            features['organ_match'],
                            features['age_compatible'],
                            features['distance_normalized'],
                            features['urgency_weight'],
                            features['reliability_score'],
                            features['freshness_score'],
                            features['compatibility_score']
                        ]
                        match_probability = self.ml_model.predict_proba([feature_vector])[0][1]
                    except Exception as e:
                        print(f"⚠️ ML prediction error: {str(e)}")
                        match_probability = compatibility_score
                
                # Final score (hybrid: rule-based + ML)
                final_score = (
                    compatibility_score * 0.4 +
                    match_probability * 0.3 +
                    urgency_weight * 0.2 +
                    reliability * 0.1
                )
                
                # Create match object
                match_data = {
                    'donor': donor,
                    'donor_id': donor.id,
                    'compatibility_score': round(compatibility_score, 3),
                    'distance_km': distance_km,
                    'match_probability': round(match_probability, 3),
                    'urgency_weight': round(urgency_weight, 3),
                    'final_score': round(final_score, 3),
                    'blood_compatible': blood_compatible,
                    'organ_match': organ_match,
                    'age_compatible': age_compatible,
                    'features': features
                }
                
                matches.append(match_data)
            
            # Sort by final score (descending)
            matches.sort(key=lambda x: x['final_score'], reverse=True)
            
            # Limit results
            matches = matches[:max_results]
            
            # Save matches to database if SOS case exists
            if sos_case_id:
                for match_data in matches:
                    match_record = Match(
                        sos_case_id=sos_case_id,
                        donor_id=match_data['donor_id'],
                        compatibility_score=match_data['compatibility_score'],
                        distance_km=match_data['distance_km'],
                        match_probability=match_data['match_probability'],
                        urgency_weight=match_data['urgency_weight'],
                        final_score=match_data['final_score'],
                        blood_compatible=match_data['blood_compatible'],
                        organ_match=match_data['organ_match'],
                        age_compatible=match_data['age_compatible'],
                        status='pending'
                    )
                    session.add(match_record)
                
                session.commit()
            
            return matches
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error in matching: {str(e)}")
            return []
        finally:
            session.close()
    
    def get_match_explanation(self, match_data):
        """Generate human-readable explanation for a match"""
        explanations = []
        
        if match_data['blood_compatible']:
            explanations.append("✓ Blood group compatible")
        else:
            explanations.append("✗ Blood group incompatible")
        
        if match_data['organ_match']:
            explanations.append("✓ Organ type matches")
        
        if match_data['age_compatible']:
            explanations.append("✓ Age compatible")
        
        if match_data['distance_km'] is not None:
            explanations.append(f"📍 Distance: {match_data['distance_km']:.1f} km")
        
        explanations.append(f"🎯 Match Score: {match_data['final_score']:.2f}/1.0")
        
        return " | ".join(explanations)

if __name__ == "__main__":
    # Test matching engine
    engine = MatchingEngine()
    print("✅ Matching engine initialized")
