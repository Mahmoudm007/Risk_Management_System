import sys
from PyQt5 import QtWidgets, QtCore
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import wordnet
import difflib
from collections import defaultdict
# Download necessary NLTK data
nltk.download('wordnet')
nltk.download('punkt')


# Functions for the search algorithm
def normalize_terms(search_terms):
    tokens = nltk.word_tokenize(search_terms)
    tokens = [token.lower() for token in tokens]
    stemmer = PorterStemmer()
    normalized_tokens = [stemmer.stem(token) for token in tokens]
    return normalized_tokens


def get_synonyms(term):
    synonyms = set()
    for syn in wordnet.synsets(term):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower())
    return synonyms


def expand_terms(tokens):
    expanded_terms = set(tokens)
    for token in tokens:
        expanded_terms.update(get_synonyms(token))
    return expanded_terms


def create_inverted_index(documents):
    inverted_index = defaultdict(list)
    for doc_id, content in documents.items():
        tokens = normalize_terms(content)
        for token in tokens:
            inverted_index[token].append(doc_id)
    return inverted_index


def search_documents(search_terms, inverted_index, documents):
    tokens = normalize_terms(search_terms)
    expanded_terms = expand_terms(tokens)
    results = set()
    for term in expanded_terms:
        if term in inverted_index:
            results.update(inverted_index[term])
        else:
            for word in inverted_index.keys():
                if difflib.get_close_matches(term, [word]):
                    results.update(inverted_index[word])
    return results


def rank_and_highlight(results, search_terms, documents, scores):
    search_terms = normalize_terms(search_terms)
    ranked_results = []
    for doc_id in results:
        content = documents[doc_id]
        score = scores.get(doc_id, 0) + sum(content.lower().count(term) for term in search_terms)
        ranked_results.append((score, doc_id, content))
    ranked_results.sort(reverse=True, key=lambda x: x[0])
    highlighted_results = [(doc_id, highlight_terms(content, search_terms), score) for score, doc_id, content in ranked_results]
    return highlighted_results


def highlight_terms(content, search_terms):
    highlighted_content = ""
    for word in content.split():
        if any(term in word.lower() for term in search_terms):
            highlighted_content += f" *{word}* "
        else:
            highlighted_content += f" {word} "
    return highlighted_content


sequence_of_event_documents = {
    1: "The ventilator utilizes an ultrasonic humidifier to humidify the inspired gases delivered to the patient's airway.",
    2: "Due to inadequate maintenance or cleaning procedures, biofilm accumulates on the surfaces of the ultrasonic components, including the transducer and water reservoir.",
    3: "A ventilator with compromised enclosure integrity experiences an electrical fault within its internal components. As a result of the fault, electrical current leaks from the internal circuitry to the metal enclosure of the ventilator.",
    4: "Ventilator is placed near a magnetic resonance imaging (MRI) machine during routine patient care. The proximity of the ventilator to the MRI machine exposes its electronic components to the magnetic fields.",
    5: "In a healthcare facility, a ventilator is located in an area with low humidity levels, such as an operating room or intensive care unit. As a result of low humidity, static electricity builds up on the surfaces of the ventilator and its components.",
    6: "During a power surge or electrical malfunction, the voltage supplied to the ventilator exceeds safe levels, leading to an overvoltage condition in the device.",
    7: "Incorrect installation of patient arm support causes discomfort and potential injury.",
    8: "During routine ventilator care in a healthcare facility, a compromised connector within the ventilator's fluid pathway fails to contain the pressurized oxygen supply properly.",
    9: "Continuous movement over various surfaces, especially rough or abrasive ones, leads to the gradual wear of castor wheels.",
    10: "A ventilator's internal fan, responsible for generating airflow, develops an imbalance, leading to excessive vibration of the fan blades and surrounding components. Over time, the vibration becomes more pronounced, causing the ventilator housing and nearby components to vibrate noticeably during use.",
    11: "During transportation, a ventilator's flexible tubing, which connects the ventilator to the patient interface, becomes kinked.",
    12: "During patient repositioning or movement within the healthcare facility, a ventilator's power cord becomes compressed or pinched between the patient's bed and a heavy piece of medical equipment.",
    13: "During routine maintenance, a healthcare provider inadvertently places their fingers or hand in a location where moving parts or sharp edges are present.",
    14: "During an emergency situation, a healthcare provider accidentally pushes the ventilator. The monitor screen, extending beyond the ventilator's body, strikes the wall with force.",
    15: "Over time, due to repeated cycles of operation and mechanical wear, the tension spring experiences increased stress levels beyond its designed limits.",
    16: "As the tension spring approaches its fatigue limit, it undergoes plastic deformation, loses its elasticity, and ultimately fails.",
    17: "During the cleaning procedure, healthcare personnel inadvertently use caustic or corrosive cleaning agents on ventilator components.",
    18: "Ventilator surfaces become contaminated with pyrogenic substances through contact with contaminated hands.",
    19: "In the assembly of a ventilator, adhesive solvents are used to bond various components together, such as plastic housing panels or electronic circuitry. Solvent vapors accumulate in the air.",
    20: "In the manufacturing process of a ventilator, lead-based solder is used to join electronic components on circuit boards and coatings on metal parts. Coatings degrade over time due to wear and corrosion.",
    21: "In a ventilator, silica gel desiccants are incorporated into the device's internal compartments or filter housings to prevent moisture buildup. Silica gel desiccants release fine silica particles into the air.",
    22: "An incorrect software update causes a malfunction in the ventilator's alarm system.",
    23: "Frequent vibrations from a nearby machinery cause loose connections in the ventilator's wiring.",
    24: "A sudden change in ambient temperature affects the ventilator's internal components, leading to reduced efficiency.",
    25: "A mechanical part in the ventilator, such as a lever or knob, becomes detached during regular use.",
    26: "The ventilator’s power supply cord is damaged, leading to intermittent power loss.",
    27: "Improperly sealed ventilator components allow dust and debris to enter and interfere with the device's operation.",
    28: "A software bug introduces delays in the ventilator's response to user commands.",
    29: "The ventilator’s fan is obstructed by foreign objects, causing overheating of the device.",
    30: "Water leakage from the humidifier component causes short circuits in the ventilator’s electronics."
}

hazardous_situation_documents = {
    1: "The patient is exposed to contaminated air.",
    2: "Ventilator is placed near the patient, risking direct exposure.",
    3: "Healthcare provider comes into contact with exposed wiring while handling the ventilator.",
    4: "Patient comes into contact with a component of the ventilator that is carrying leakage current.",
    5: "Healthcare provider comes into contact with the grounded chassis or housing of the ventilator while it is leaking current to the ground.",
    6: "A healthcare provider, unaware of the electrical fault, touches the external surface of the ventilator enclosure while adjusting settings.",
    7: "This interference disrupts the ventilator's functionality, leading to incorrect readings, erratic operation, or complete failure of the device.",
    8: "An ESD event occurs near sensitive electronic components of the ventilator, causing damage to the electronic circuitry.",
    9: "The overvoltage condition can cause damage to the electrical components of the ventilator, including circuit boards, sensors, and control mechanisms.",
    10: "Patient arm dislodged and fell on the patient.",
    11: "Pressurized oxygen escapes from the ventilator system in a sudden burst, leading to the injection of oxygen into the eye of a healthcare provider who was adjusting the ventilator settings.",
    12: "Reduced mobility impacts the accessibility of the ventilator in emergency situations.",
    13: "A healthcare provider, while adjusting the ventilator settings or performing routine maintenance, comes into contact with the vibrating housing or components.",
    14: "This bending restricts the flow of air or oxygen through the tubing, compromising the delivery of respiratory support to the patient.",
    15: "As a result of the compressed power cord, the electrical connection to the ventilator is disrupted. This leads to a loss of power supply to the ventilator, causing it to shut down unexpectedly and interrupting respiratory support to the patient.",
    16: "The moving parts or sharp edges within the ventilator come into contact with the healthcare provider's hand or fingers, causing lacerations, cuts, or abrasions.",
    17: "Impaired monitor functionality, readability, or structural integrity. This could affect the accuracy of patient monitoring data displayed on the screen, leading to potential errors in clinical decision-making.",
    18: "The valve mechanism fails to operate properly, causing irregularities in the flow of respiratory gases.",
    19: "The cleaning agents used are not properly diluted and corrode metal surfaces, compromising the functionality of the ventilator.",
    20: "Pyrogens present on the ventilator's surfaces potentially transfer to tubing and connectors.",
    21: "Healthcare provider working in proximity to the ventilator assembly area inhales these vapors.",
    22: "Inhalation of dust particles released from malfunctioning ventilator components.",
    23: "Electrical shorts caused by water ingress in the ventilator.",
    24: "Exposure to high levels of noise from malfunctioning ventilator fans.",
    25: "Risk of fire due to overheating of the ventilator’s power supply.",
    26: "Physical injury from sharp edges of broken ventilator components.",
    27: "Health hazards from exposure to chemical fumes during cleaning procedures.",
    28: "Risk of infection from improperly sterilized ventilator parts.",
    29: "Inadequate patient ventilation due to obstructed airways in the device.",
    30: "Accidental ingestion of small parts or components by the patient or healthcare provider."
}

control_documents = {
    1: "Hazardous situation in software design requires careful planning and execution.",
    2: "Risk analysis should be an integral part of hazardous situation design.",
    3: "Electrical hazards must be identified and mitigated.",
    4: "Mechanical designs need to comply with safety standards.",
    5: "Comprehensive testing ensures system reliability in hazardous situations.",
    6: "Regular maintenance schedules should be adhered to for all critical components.",
    7: "Proper training should be provided for handling and maintaining ventilator systems.",
    8: "Implement redundancy in safety-critical systems to prevent single points of failure.",
    9: "Ensure proper insulation and grounding of electrical components.",
    10: "Utilize non-corrosive materials for external and internal components exposed to environmental factors.",
    11: "Develop protocols for emergency procedures and equipment failures.",
    12: "Verify the accuracy of all monitoring devices through regular calibration.",
    13: "Establish quality control measures during the manufacturing process.",
    14: "Conduct thorough inspections and tests after any maintenance or repair work.",
    15: "Develop and implement a risk management framework for all critical systems.",
    16: "Ensure that all components meet regulatory standards and certifications.",
    17: "Monitor and address any potential sources of contamination in the device environment.",
    18: "Implement safeguards to prevent and mitigate the effects of electrical surges.",
    19: "Establish protocols for handling hazardous substances used in device manufacturing.",
    20: "Regularly review and update safety procedures to reflect new risks and technological advancements.",
    21: "Ensure clear labeling and documentation of all safety features and maintenance requirements.",
    22: "Integrate automated monitoring systems to detect early signs of system failure.",
    23: "Develop comprehensive documentation for all maintenance activities to ensure traceability.",
    24: "Implement robust cybersecurity measures to protect against data breaches and unauthorized access.",
    25: "Conduct regular training sessions on safety and emergency procedures for all personnel.",
    26: "Establish a system for reporting and addressing safety incidents and near-misses.",
    27: "Utilize advanced simulation tools to predict and mitigate potential system failures.",
    28: "Ensure compatibility of all components with current safety and performance standards.",
    29: "Implement procedures for the safe disposal of obsolete or damaged components.",
    30: "Develop guidelines for maintaining and testing backup power supplies to ensure reliability during outages.",
    31: "Evaluate and mitigate risks associated with the use of new technologies and materials in device design.",
    32: "Collaborate with external experts to validate safety protocols and procedures.",
    33: "Conduct periodic audits to ensure compliance with safety regulations and industry standards.",
    34: "Implement systems for tracking and managing spare parts and replacement components.",
    35: "Develop contingency plans for handling unforeseen equipment failures or emergencies."
}


harm_description_documents = {
    1: "Hearing impairmnet ",
    2: "Respiratory infections",
    3: "Electric shock ",
    4: "Burn ",
    5: "respiratory distress",
    6: "malfunctions",
    7: "Complete failure of the ventilator.",
    8: "striking the patient's body, limbs, or face.",
    9: "tissue damage",
    10: "Deterioration of health ",
    11: "repetitive strain injuries (RSIs)/ discomfort",
    12: "Hypoxia ",
    13: "respiratory failure",
    14: "cuts",
    15: "fever ",
    16: "respiratory irritation",
    17: "Neurological damage",
    18: "Silicosis",
    19: "Anaphylaxis",
    20: "damage to the healthcare provider's reputation.",
}

# Create separate inverted indices for each set of documents
sequence_of_event_inverted_index = create_inverted_index(sequence_of_event_documents)
hazardous_situation_inverted_index = create_inverted_index(hazardous_situation_documents)
control_inverted_index = create_inverted_index(control_documents)
harm_description_inverted_index = create_inverted_index(harm_description_documents)
# Scores for ranking
scores = defaultdict(int)

