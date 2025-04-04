
from pyrogram import Client, filters
from pyrogram.types import Message
from fuzzywuzzy import process
import asyncio
import logging
from logging.handlers import RotatingFileHandler
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'yakeen_bot.log',
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=3
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Channel IDs
YAKEEN_MAIN = -1002544207724  # Yakeen 2.0 main channel
PHYSICS_CHANNEL = -1002589768419
PHYSICAL_CHEM_CHANNEL = -1002508704907
IOC_CHANNEL = -1002508704907
OC_CHANNEL = -1002508704907
BOTANY_CHANNEL = -1005555555555
ZOOLOGY_CHANNEL = -1006666666666

# Message queue for maintaining sequence
message_queue = asyncio.Queue() 

async def process_queue():
    """Process messages in sequence with logging"""
    while True:
        message, target_channel = await message_queue.get()
        try:
            await message.copy(target_channel)
            logger.info(
                f"Successfully forwarded message to channel {target_channel}. "
                f"Original message ID: {message.id}"
            )
        except Exception as e:
            logger.error(
                f"Failed to forward message ID {message.id} to channel {target_channel}. "
                f"Error: {str(e)}",
                exc_info=True
            )
        finally:
            message_queue.task_done()

def find_best_match(text, choices, threshold=75):
    """Find the best matching chapter with logging"""
    try:
        result = process.extractOne(text.lower(), [c.lower() for c in choices])
        if result and result[1] >= threshold:
            matched_chapter = choices[result[2]]
            logger.debug(
                f"Matched '{text[:50]}...' to '{matched_chapter}' "
                f"with confidence {result[1]}%"
            )
            return matched_chapter
        logger.debug(f"No good match found for '{text[:50]}...' (best match: {result[1] if result else 'N/A'}%)")
        return None
    except Exception as e:
        logger.error(f"Error in find_best_match for text '{text[:50]}...': {str(e)}", exc_info=True)
        return None

@Client.on_message(filters.chat(YAKEEN_MAIN))
async def sort_messages(client: Client, message: Message):
    """Handle incoming messages with logging"""
    try:
        caption = message.caption if message.caption else message.text
        
        if not caption:
            logger.debug(f"Received message {message.id} with no caption/text")
            return
            
        if message_queue.empty():
            asyncio.create_task(process_queue())
            logger.info("Started message queue processor")
        
        best_match = find_best_match(caption, ALL_CHAPTERS)
        
        if best_match:
            target_channel = CHAPTER_MAPPING[best_match.lower()]
            await message_queue.put((message, target_channel))
            logger.info(
                f"Queued message ID {message.id} for forwarding to {target_channel}. "
                f"Matched chapter: '{best_match}'"
            )
        else:
            logger.warning(
                f"No chapter match found for message ID {message.id}. "
                f"Content: '{caption[:100]}...'"
            )
    
    except Exception as e:
        logger.error(
            f"Error processing message ID {message.id}: {str(e)}",
            exc_info=True
        )




# Chapter mappings with slight variations for fuzzy matching
PHYSICS_CHAPTERS = [
    "Basic Maths & Calculus (Mathematical Tools)",
    "Vectors",
    "Units and Measurements",
    "Motion in a straight line",
    "Motion in a plane",
    "Laws of motion",
    "Work, energy and power",
    "Centre of mass and System of Particles",
    "Rotational Motion",
    "Gravitation",
    "Mechanical Properties of Solids",
    "Mechanical Properties of Fluids",
    "Thermal Properties of matter",
    "Kinetic Theory",
    "Thermodynamics",
    "Oscillations",
    "Waves",
    "Electric Charges and Fields",
    "Electrostatic Potential and Capacitance",
    "Current Electricity",
    "Moving Charges and Magnetism",
    "Magnetism and Matter",
    "Electromagnetic Induction",
    "Alternating Current",
    "Electromagnetic Waves",
    "Ray Optics and Optical Instruments",
    "Wave Optics",
    "Dual Nature of Radiation and Matter",
    "Atoms",
    "Nuclei",
    "Semiconductor Electronics: Materials, Devices and Simple Circuits"
]

PHYSICAL_CHEM_CHAPTERS = [
    "Some Basic Concept of Chemistry",
    "Redox Reaction",
    "Solutions",
    "State of Matter",
    "Thermodynamics",
    "Thermochemistry",
    "Chemical Equilibrium",
    "Ionic Equilibrium",
    "Electrochemistry",
    "Chemical Kinetics",
    "Structure of Atom",
    "Practical Physical Chemistry"
]

IOC_CHAPTERS = [
    "Classification of Elements and Periodicity in Properties",
    "Chemical Bonding and Molecular Structure",
    "Co-ordination Compound",
    "Coordination Compound",
    "The d and f Block Elements",
    "The p-block Elements",
    "Salt Analysis"
]

OC_CHAPTERS = [
    "Organic Chemistry: Some Basic principles and Techniques (IUPAC Naming)",
    "Organic Chemistry: Some Basic principles and Techniques (Isomerism)",
    "Organic Chemistry: Some Basic principles and Techniques (GOC)",
    "Hydrocarbon",
    "Halosilkanes and Haloarenes",
    "Alcohols, Ethers and Phenols",
    "Aldehydes, Ketones and Carboxylic Acids",
    "Amines",
    "Biomolecules",
    "Practical Organic Chemistry"
]

BOTANY_CHAPTERS = [
    "Cell - The Unit of Life",
    "Cell Cycle and Cell Division",
    "The Living World",
    "Biological Classification",
    "Plant Kingdom",
    "Morphology of Flowering Plants",
    "Anatomy of Flowering Plants",
    "Respiration in Plants",
    "Photosynthesis in Higher Plants",
    "Plant Growth and Development",
    "Sexual Reproduction in Flowering Plant",
    "Molecular Basis of Inheritance",
    "Principle of Inheritance and Variation",
    "Microbes in Human Welfare",
    "Organisms and Population",
    "Ecosystem",
    "Biodiversity and Conservation"
]

ZOOLOGY_CHAPTERS = [
    "Structural Organization in Animals",
    "Breathing and Exchange of Gases",
    "Body Fluids and Circulation",
    "Excretory Products & their Elimination",
    "Locomotion & Movement",
    "Neural Control & Coordination",
    "Chemical Coordination & Integration",
    "Animal Kingdom",
    "Biomolecules",
    "Human Reproduction",
    "Reproduction Health",
    "Human Health and Diseases",
    "Biotechnology: Principles & Processes",
    "Biotechnology and its Applications",
    "Evolution"
]

# Create a mapping of all chapters to their respective channels
CHAPTER_MAPPING = {}
for chapter in PHYSICS_CHAPTERS:
    CHAPTER_MAPPING[chapter.lower()] = PHYSICS_CHANNEL

for chapter in PHYSICAL_CHEM_CHAPTERS:
    CHAPTER_MAPPING[chapter.lower()] = PHYSICAL_CHEM_CHANNEL

for chapter in IOC_CHAPTERS:
    CHAPTER_MAPPING[chapter.lower()] = IOC_CHANNEL

for chapter in OC_CHAPTERS:
    CHAPTER_MAPPING[chapter.lower()] = OC_CHANNEL

for chapter in BOTANY_CHAPTERS:
    CHAPTER_MAPPING[chapter.lower()] = BOTANY_CHANNEL

for chapter in ZOOLOGY_CHAPTERS:
    CHAPTER_MAPPING[chapter.lower()] = ZOOLOGY_CHANNEL

# Combine all chapters for fuzzy matching
ALL_CHAPTERS = (PHYSICS_CHAPTERS + PHYSICAL_CHEM_CHAPTERS + 
                IOC_CHAPTERS + OC_CHAPTERS + 
                BOTANY_CHAPTERS + ZOOLOGY_CHAPTERS)

