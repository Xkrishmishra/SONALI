async def init_all_components():
    import asyncio

    # Your initialization functions for dirr, git, dbb, and heroku
    await asyncio.gather(
        init_dirr(),
        init_git(),
        init_dbb(),
        init_heroku()
    )

# Call the init_all_components function to initialize everything concurrently
if __name__ == '__main__':
    asyncio.run(init_all_components())