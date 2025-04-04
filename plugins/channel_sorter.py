from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import logging
from logging.handlers import RotatingFileHandler

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
IOC_CHANNEL = -1002508704907  # Changed to unique ID
OC_CHANNEL = -1002508704907   # Changed to unique ID
BOTANY_CHANNEL = -1002572646577
ZOOLOGY_CHANNEL = -1002572646577

# Message queue for maintaining sequence
message_queue = asyncio.Queue()

# Chapter mappings (simplified exact matching)
CHAPTER_MAPPING = {
    # Physics
    "basic maths & calculus (mathematical tools)": PHYSICS_CHANNEL,
    "vectors": PHYSICS_CHANNEL,
    "units and measurements": PHYSICS_CHANNEL,
    "motion in a straight line": PHYSICS_CHANNEL,
    "motion in a plane": PHYSICS_CHANNEL,
    "laws of motion": PHYSICS_CHANNEL,
    "work, energy and power": PHYSICS_CHANNEL,
    "centre of mass and system of particles": PHYSICS_CHANNEL,
    "rotational motion": PHYSICS_CHANNEL,
    "gravitation": PHYSICS_CHANNEL,
    "mechanical properties of solids": PHYSICS_CHANNEL,
    "mechanical properties of fluids": PHYSICS_CHANNEL,
    "thermal properties of matter": PHYSICS_CHANNEL,
    "kinetic theory": PHYSICS_CHANNEL,
    "thermodynamics": PHYSICS_CHANNEL,
    "oscillations": PHYSICS_CHANNEL,
    "waves": PHYSICS_CHANNEL,
    "electric charges and fields": PHYSICS_CHANNEL,
    "electrostatic potential and capacitance": PHYSICS_CHANNEL,
    "current electricity": PHYSICS_CHANNEL,
    "moving charges and magnetism": PHYSICS_CHANNEL,
    "magnetism and matter": PHYSICS_CHANNEL,
    "electromagnetic induction": PHYSICS_CHANNEL,
    "alternating current": PHYSICS_CHANNEL,
    "electromagnetic waves": PHYSICS_CHANNEL,
    "ray optics and optical instruments": PHYSICS_CHANNEL,
    "wave optics": PHYSICS_CHANNEL,
    "dual nature of radiation and matter": PHYSICS_CHANNEL,
    "atoms": PHYSICS_CHANNEL,
    "nuclei": PHYSICS_CHANNEL,
    "semiconductor electronics: materials, devices and simple circuits": PHYSICS_CHANNEL,
    
    # Physical Chemistry
    "some basic concept of chemistry": PHYSICAL_CHEM_CHANNEL,
    "redox reaction": PHYSICAL_CHEM_CHANNEL,
    "solutions": PHYSICAL_CHEM_CHANNEL,
    "state of matter": PHYSICAL_CHEM_CHANNEL,
    "thermodynamics": PHYSICAL_CHEM_CHANNEL,
    "thermochemistry": PHYSICAL_CHEM_CHANNEL,
    "chemical equilibrium": PHYSICAL_CHEM_CHANNEL,
    "ionic equilibrium": PHYSICAL_CHEM_CHANNEL,
    "electrochemistry": PHYSICAL_CHEM_CHANNEL,
    "chemical kinetics": PHYSICAL_CHEM_CHANNEL,
    "structure of atom": PHYSICAL_CHEM_CHANNEL,
    "practical physical chemistry": PHYSICAL_CHEM_CHANNEL,
    
    # IOC
    "classification of elements and periodicity in properties": IOC_CHANNEL,
    "chemical bonding and molecular structure": IOC_CHANNEL,
    "co-ordination compound": IOC_CHANNEL,
    "coordination compound": IOC_CHANNEL,
    "the d and f block elements": IOC_CHANNEL,
    "the p-block elements": IOC_CHANNEL,
    "salt analysis": IOC_CHANNEL,
    
    # OC
    "organic chemistry: some basic principles and techniques (iupac naming)": OC_CHANNEL,
    "organic chemistry: some basic principles and techniques (isomerism)": OC_CHANNEL,
    "organic chemistry: some basic principles and techniques (goc)": OC_CHANNEL,
    "hydrocarbon": OC_CHANNEL,
    "halosilkanes and haloarenes": OC_CHANNEL,
    "alcohols, ethers and phenols": OC_CHANNEL,
    "aldehydes, ketones and carboxylic acids": OC_CHANNEL,
    "amines": OC_CHANNEL,
    "biomolecules": OC_CHANNEL,
    "practical organic chemistry": OC_CHANNEL,
    
    # Botany
    "cell - the unit of life": BOTANY_CHANNEL,
    "cell cycle and cell division": BOTANY_CHANNEL,
    "the living world": BOTANY_CHANNEL,
    "biological classification": BOTANY_CHANNEL,
    "plant kingdom": BOTANY_CHANNEL,
    "morphology of flowering plants": BOTANY_CHANNEL,
    "anatomy of flowering plants": BOTANY_CHANNEL,
    "respiration in plants": BOTANY_CHANNEL,
    "photosynthesis in higher plants": BOTANY_CHANNEL,
    "plant growth and development": BOTANY_CHANNEL,
    "sexual reproduction in flowering plant": BOTANY_CHANNEL,
    "molecular basis of inheritance": BOTANY_CHANNEL,
    "principle of inheritance and variation": BOTANY_CHANNEL,
    "microbes in human welfare": BOTANY_CHANNEL,
    "organisms and population": BOTANY_CHANNEL,
    "ecosystem": BOTANY_CHANNEL,
    "biodiversity and conservation": BOTANY_CHANNEL,
    
    # Zoology
    "structural organization in animals": ZOOLOGY_CHANNEL,
    "breathing and exchange of gases": ZOOLOGY_CHANNEL,
    "body fluids and circulation": ZOOLOGY_CHANNEL,
    "excretory products & their elimination": ZOOLOGY_CHANNEL,
    "locomotion & movement": ZOOLOGY_CHANNEL,
    "neural control & coordination": ZOOLOGY_CHANNEL,
    "chemical coordination & integration": ZOOLOGY_CHANNEL,
    "animal kingdom": ZOOLOGY_CHANNEL,
    "biomolecules": ZOOLOGY_CHANNEL,
    "human reproduction": ZOOLOGY_CHANNEL,
    "reproduction health": ZOOLOGY_CHANNEL,
    "human health and diseases": ZOOLOGY_CHANNEL,
    "biotechnology: principles & processes": ZOOLOGY_CHANNEL,
    "biotechnology and its applications": ZOOLOGY_CHANNEL,
    "evolution": ZOOLOGY_CHANNEL
}

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

def find_chapter_match(text):
    """Find matching chapter using exact matching (case insensitive)"""
    text_lower = text.lower().strip()
    for chapter in CHAPTER_MAPPING:
        if chapter in text_lower:
            logger.debug(f"Found match: '{chapter}' in message text")
            return chapter
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
        
        matched_chapter = find_chapter_match(caption)
        
        if matched_chapter:
            target_channel = CHAPTER_MAPPING[matched_chapter]
            await message_queue.put((message, target_channel))
            logger.info(
                f"Queued message ID {message.id} for forwarding to {target_channel}. "
                f"Matched chapter: '{matched_chapter}'"
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

app = Client("yakeen_bot")

if __name__ == "__main__":
    logger.info("Starting Yakeen NEET 2.0 Bot...")
    try:
        app.run()
        logger.info("Bot stopped gracefully")
    except Exception as e:
        logger.critical(f"Bot crashed: {str(e)}", exc_info=True)
    finally:
        logger.info("Bot process ended")
