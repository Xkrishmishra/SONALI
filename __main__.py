import asyncio

async def load_plugin(module):
    # Function to load a single plugin module
    await module.initialize()

async def load_plugins(modules):
    # Function to load all plugin modules in parallel
    await asyncio.gather(*(load_plugin(module) for module in modules))

async def async_init(modules):
    # New async init function for faster startup
    await load_plugins(modules)

# Assuming the rest of your original code follows here...