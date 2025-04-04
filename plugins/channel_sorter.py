from pyrogram import Client, filters
from pyrogram.types import Message

# Channel IDs
MAIN_CHANNEL_ID = -1002544207724  # Replace with your main channel ID
PHYSICS_CHANNEL_ID = -1002589768419  # Replace with physics channel ID
CHEMISTRY_CHANNEL_ID = -1002508704907  # Replace with chemistry channel ID

# Channel mapping dictionary
CHANNEL_MAPPING = {
    # Physics Chapters (NEET Syllabus)
    "physics": PHYSICS_CHANNEL_ID,
    "mechanics": PHYSICS_CHANNEL_ID,
    "electrodynamics": PHYSICS_CHANNEL_ID,
    "optics": PHYSICS_CHANNEL_ID,
    "thermodynamics": PHYSICS_CHANNEL_ID,
    "modern physics": PHYSICS_CHANNEL_ID,
    "kinematics": PHYSICS_CHANNEL_ID,
    "laws of motion": PHYSICS_CHANNEL_ID,
    "work energy power": PHYSICS_CHANNEL_ID,
    "rotational motion": PHYSICS_CHANNEL_ID,
    "gravitation": PHYSICS_CHANNEL_ID,
    "properties of matter": PHYSICS_CHANNEL_ID,
    "oscillations": PHYSICS_CHANNEL_ID,
    "waves": PHYSICS_CHANNEL_ID,
    "electrostatics": PHYSICS_CHANNEL_ID,
    "current electricity": PHYSICS_CHANNEL_ID,
    "magnetic effects": PHYSICS_CHANNEL_ID,
    "electromagnetic induction": PHYSICS_CHANNEL_ID,
    "alternating current": PHYSICS_CHANNEL_ID,
    "electromagnetic waves": PHYSICS_CHANNEL_ID,
    "ray optics": PHYSICS_CHANNEL_ID,
    "wave optics": PHYSICS_CHANNEL_ID,
    "dual nature": PHYSICS_CHANNEL_ID,
    "atoms nuclei": PHYSICS_CHANNEL_ID,
    "semiconductors": PHYSICS_CHANNEL_ID,
    
    # Chemistry Chapters (NEET Syllabus)
    "chemistry": CHEMISTRY_CHANNEL_ID,
    "physical chemistry": CHEMISTRY_CHANNEL_ID,
    "inorganic chemistry": CHEMISTRY_CHANNEL_ID,
    "organic chemistry": CHEMISTRY_CHANNEL_ID,
    "atomic structure": CHEMISTRY_CHANNEL_ID,
    "chemical bonding": CHEMISTRY_CHANNEL_ID,
    "thermodynamics": CHEMISTRY_CHANNEL_ID,
    "equilibrium": CHEMISTRY_CHANNEL_ID,
    "redox reactions": CHEMISTRY_CHANNEL_ID,
    "solid state": CHEMISTRY_CHANNEL_ID,
    "solutions": CHEMISTRY_CHANNEL_ID,
    "electrochemistry": CHEMISTRY_CHANNEL_ID,
    "chemical kinetics": CHEMISTRY_CHANNEL_ID,
    "surface chemistry": CHEMISTRY_CHANNEL_ID,
    "periodic table": CHEMISTRY_CHANNEL_ID,
    "p block": CHEMISTRY_CHANNEL_ID,
    "d block": CHEMISTRY_CHANNEL_ID,
    "coordination compounds": CHEMISTRY_CHANNEL_ID,
    "metallurgy": CHEMISTRY_CHANNEL_ID,
    "hydrocarbons": CHEMISTRY_CHANNEL_ID,
    "haloalkanes": CHEMISTRY_CHANNEL_ID,
    "alcohols": CHEMISTRY_CHANNEL_ID,
    "aldehydes": CHEMISTRY_CHANNEL_ID,
    "carboxylic acids": CHEMISTRY_CHANNEL_ID,
    "amines": CHEMISTRY_CHANNEL_ID,
    "biomolecules": CHEMISTRY_CHANNEL_ID,
    "polymers": CHEMISTRY_CHANNEL_ID,
    "chemistry in everyday life": CHEMISTRY_CHANNEL_ID,
    
    # Add more mappings as needed
}

@Client.on_message(filters.chat(MAIN_CHANNEL_ID))
async def sort_messages(client: Client, message: Message):
    """Handle incoming messages from the main channel"""
    try:
        # Get caption (for media) or text (for text messages)
        caption = message.caption if message.caption else message.text
        
        if not caption:
            return  # Skip if no caption/text
        
        caption_lower = caption.lower()
        
        # Check for keywords in the caption
        for keyword, channel_id in CHANNEL_MAPPING.items():
            if keyword.lower() in caption_lower:
                # Forward the message to the appropriate channel
                await message.forward(channel_id)
                print(f"Forwarded message to {keyword} channel")
                break
    
    except Exception as e:
        print(f"Error processing message: {e}")
