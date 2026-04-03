<p align="center">
    <a href="https://github.com/KurimuzonAkuma/pyrogram">
        <img src="https://raw.githubusercontent.com/KurimuzonAkuma/kurigramartwork/master/kurigram-logo.png" alt="Pyrogram" width="128">
    </a>
    <br>
    <b>Telegram MTProto API Framework for Python</b>
    <br>
    <a href="https://kurigram.icu">
        Homepage
    </a>
    •
    <a href="https://docs.kurigram.icu">
        Documentation
    </a>
    •
    <a href="https://t.me/kurigram_news">
        News
    </a>
    •
    <a href="https://t.me/kurigram_chat">
        Chat
    </a>
</p>

## Pyrogram

> Elegant, modern and asynchronous Telegram MTProto API framework in Python for users and bots

``` python
from pyrogram import Client, filters

app = Client("my_account")


@app.on_message(filters.private)
async def hello(client, message):
    await message.reply("Hello from Pyrogram!")


app.run()
```

**Pyrogram** is a modern, elegant and asynchronous [MTProto API](https://docs.kurigram.icu/topics/mtproto-vs-botapi)
framework. It enables you to easily interact with the main Telegram API through a user account (custom client) or a bot
identity (bot API alternative) using Python.

### Support

If you'd like to support my fork, you can consider:

- `kurimuzonakuma.ton` - TON
- `TCbZ7CSpTvTJ6rno2eoWWYBx7hmYF75wk3` - USDT TRC20

### Key Features

- **Ready**: Install Pyrogram with pip and start building your applications right away.
- **Easy**: Makes the Telegram API simple and intuitive, while still allowing advanced usages.
- **Elegant**: Low-level details are abstracted and re-presented in a more convenient way.
- **Fast**: Boosted up by [TgCrypto](https://github.com/pyrogram/tgcrypto), a high-performance cryptography library written in C.
- **Type-hinted**: Types and methods are all type-hinted, enabling excellent editor support.
- **Async**: Fully asynchronous (also usable synchronously if wanted, for convenience).
- **Powerful**: Full access to Telegram's API to execute any official client action and more.

### Installing

Stable version

``` bash
pip3 install kurigram
```

Dev version
``` bash
pip3 install https://github.com/KurimuzonAkuma/kurigram/archive/dev.zip --force-reinstall
```

### Resources

- Check out the [docs](https://docs.kurigram.icu) to learn more about Pyrogram, get started right
away and discover more in-depth material for building your client applications.
- Join the [official channel](https://t.me/kurigram_news) and stay tuned for news, updates and announcements.
- Join the [official chat](https://t.me/kurigram_chat) to communicate with people.
