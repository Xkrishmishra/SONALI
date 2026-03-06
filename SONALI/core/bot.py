from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus

import config
from SONALI.core.logging import LOGGER  # Fixed absolute import


class RAUSHAN(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting Bot...")
        super().__init__(
            name="SONALI",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

        try:
            await self.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b></u>\n\n"
                    f"ɪᴅ : <code>{self.id}</code>\n"
                    f"ɴᴀᴍᴇ : {self.name}\n"
                    f"ᴜsᴇʀɴᴀᴍᴇ : @{self.username}"
                ),
                parse_mode="html"
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "Bot cannot access the log group/channel. Add the bot there first."
            )
        except Exception as ex:
            LOGGER(__name__).error(
                f"Bot failed to send log message. Reason: {type(ex).__name__}."
            )

        # Check bot admin status in log group
        try:
            member = await self.get_chat_member(config.LOGGER_ID, self.id)
            if member.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).error(
                    "Promote your bot as admin in the log group/channel."
                )
        except Exception:
            LOGGER(__name__).warning("Cannot verify bot admin status in log group.")

        LOGGER(__name__).info(f"Music Bot started as {self.name}")

    async def stop(self):
        await super().stop()
