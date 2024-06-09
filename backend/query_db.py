import firebase_admin
from firebase_admin import credentials, firestore


# Path to your service account key file
cred = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()


def query_available_years():

    # Reference to the 'all_races' document in the 'races' collection
    all_races_ref = db.collection('races').document('all_races')

    # Fetch all subcollections under 'all_races'
    subcollections = all_races_ref.collections()

    # Extract the names of the subcollections, which are the years
    years = [collection.id for collection in subcollections]

    return years

def query_available_races(year):

    # Reference to the specific year subcollection under 'all_races'
    year_ref = db.collection('races').document('all_races').collection(year)

    # Fetch all documents in the year subcollection
    docs = year_ref.stream()

    # Extract the race names from the document IDs
    races = [doc.id for doc in docs]
    print(races)
    return races

def query_available_sessions(year, race):

    # Reference to the specific race document in the specified year subcollection
    session_ref = db.collection('races').document('all_races').collection(year).document(race).collection("sessions")

    # Fetch all subcollections under the race document
    sessions_st = session_ref.stream()

    # Extract the names of the subcollections, which are the sessions
    sessions = [doc.id for doc in sessions_st]

    return sessions


def query_session_info(year, race, session):

    session_doc_ref = db.collection('races').document('all_races').collection(year).document(race).collection("sessions").document(session)
    session_doc = session_doc_ref.get()

    return session_doc


def query_location_info(year, race):
    race_doc_ref = db.collection('races').document('all_races').collection(year).document(race)
    race_doc_dict = race_doc_ref.get().to_dict()

    return race_doc_dict.get("latitude"), race_doc_dict.get("longitude")