<p align="center">
    <a href="https://github.com/KurimuzonAkuma/kurigram">
        <img src="https://raw.githubusercontent.com/KurimuzonAkuma/kurigramartwork/master/kurigram-logo.png" alt="Kurigram" width="128">
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
    <br/>
    <br/>
    <a href="https://pypi.python.org/pypi/kurigram">
        <img src="https://img.shields.io/pypi/v/kurigram.svg?logo=pypi&logoColor=white" alt="PyPI package version">
    </a>
    <a href="https://pypi.python.org/pypi/kurigram">
        <img src="https://img.shields.io/pypi/l/kurigram.svg" alt="License">
    </a>
    <a href="https://pypi.python.org/pypi/kurigram">
        <img src="https://img.shields.io/pypi/pyversions/kurigram.svg" alt="Python versions">
    </a>
</p>

## Kurigram

> Elegant, modern and asynchronous Telegram MTProto API framework in Python for users and bots

Kurigram is an actively maintained pyrogram fork for Python designed as a drop-in replacement for Pyrogram, Kurigram provides support for the latest Telegram features including Gifts, Stories, Topics, Business Accounts, and more.

```python
from pyrogram import Client, filters

app = Client("my_account")


@app.on_message(filters.private)
async def hello(client, message):
    await message.reply("Hello from Kurigram!")


app.run()
```

**Kurigram** is a modern, elegant and asynchronous [MTProto API](https://docs.kurigram.icu/topics/mtproto-vs-botapi)
framework. It enables you to easily interact with the main Telegram API through a user account (custom client) or a bot
identity (bot API alternative) using Python.

### Support

Kurigram is an open source project. Your support helps us maintain and improve the library, consider supporting its development:

- `kurimuzonakuma.ton` - TON
- `TYAY3cVST3NY5mqs1M2qGV6PjXDjLLeC6v` - USDT TRC20

Thank you for supporting Kurigram ❤️

### Key Features

- **Ready**: Install Kurigram with pip and start building your applications right away.
- **Easy**: Makes the Telegram API simple and intuitive, while still allowing advanced usages.
- **Elegant**: Low-level details are abstracted and re-presented in a more convenient way.
- **Fast**: Boosted up by [TgCrypto](https://github.com/pyrogram/tgcrypto), a high-performance cryptography library written in C.
- **Type-hinted**: Types and methods are all type-hinted, enabling excellent editor support.
- **Async**: Fully asynchronous (also usable synchronously if wanted, for convenience).
- **Powerful**: Full access to Telegram's API to execute any official client action and more.

### Installing

Stable version

``` bash
pip install kurigram
```

Dev version

``` bash
pip install https://github.com/KurimuzonAkuma/kurigram/archive/dev.zip --force-reinstall
```

### Resources

- Check out the [docs](https://docs.kurigram.icu) to learn more about Kurigram, get started right
away and discover more in-depth material for building your client applications.
- Join the [official channel](https://t.me/kurigram_news) and stay tuned for news, updates and announcements.
- Join the [official chat](https://t.me/kurigram_chat) to communicate with people.
