from aiogram.types import ChatActions, MediaGroup, Message
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from bot.bot import on


options = Options()
options.headless = True

@on(command="mensa")
async def command_mensa(message: Message):
    await ChatActions.upload_photo()

    print("start selenium")
    driver = webdriver.Firefox(options=options)
    driver.get("https://www.studentenwerk-goettingen.de/campusgastronomie/mensen/speiseplaene-der-mensen")

    cc_window = driver.find_element(By.CLASS_NAME, "cc-window")
    driver.execute_script(f"""
        var e = document.getElementsByClassName("cc-window")[0];
        e.parentNode.removeChild(e);
    """)

    elem = driver.find_element(By.ID, "mensaspeiseplan")
    children = elem.find_elements(By.CLASS_NAME, "ce-bodytext")
    for i, child in enumerate(children):
        print(i, child)
        child.screenshot(f"./screenshot{i}.png")

    driver.close()
    print("close selenium")

    media = MediaGroup()
    for i in range(len(children)):
        media.attach_photo(open(f"./screenshot{i}.png", "rb"))

    await message.reply_media_group(media=media)
