from supabase import create_client
import serial
import time
import textwrap
import random
import re

SUPABASE_URL = "https://yekpasnhsxlhtdzahsme.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlla3Bhc25oc3hsaHRkemFoc21lIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjcxMzg0NywiZXhwIjoyMDg4Mjg5ODQ3fQ.ZWIUxGiDQidZxbuzCke0MO4PmG1zekc-LVtwZis7fhY"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

printer = serial.Serial("/dev/serial0", 9600, timeout=1)

PRINT_DELAY = 25

last_printed_id = None

# clean gibberish output (happens on puncuation)
def clean_text(text):

    replacements = {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "—": "-",
        "–": "-",
        "…": "...",
        "\u00a0": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)
    # chatgpt advised encoding the printer output as ascii to further imporve printing
    return text.encode(
        "ascii",
        errors="ignore"
    ).decode()

def format_letter(content, author):

    if not author:
        author = "Anonymous"

    content = clean_text(content)

# make the output look less like a shoping reciept
    wrapped = textwrap.fill(
        content,
        width=30
    )

    text = "\n\n"

    text += wrapped

    text += "\n\n\n"

    text += "— " + author

    text += "\n\n\n\n"

    return text

# ensuring that the visitor letts are priority
def get_visitor_letter():

    response = supabase.table("visitor_letters") \
        .select("*") \
        .eq("printed", False) \
        .order("created_at") \
        .limit(1) \
        .execute()

    if response.data:
        return response.data[0]

    return None


def mark_visitor_printed(letter_id):

    supabase.table("visitor_letters") \
        .update({
            "printed": True,
            "printed_at": "now()"
        }) \
        .eq("id", letter_id) \
        .execute()


# otherwise print from archive table
def get_archive_letter():

    response = supabase.table("archive_letters") \
        .select("*") \
        .order("printed_count") \
        .limit(1) \
        .execute()

    if response.data:
        return response.data[0]

    return None

# so I can see and adjust in supabase how many times certain letters are getting printed
def increment_archive_print(letter_id, current_count):

    supabase.table("archive_letters") \
        .update({
            "printed_count": current_count + 1
        }) \
        .eq("id", letter_id) \
        .execute()


# main loop
# show process in console for easy debugging
print("Starting love letter printer...")

time.sleep(2)

while True:

    # visitor letters first
    letter = get_visitor_letter()
    source = "visitor"

    # then archive letters
    if letter is None:
        letter = get_archive_letter()
        source = "archive"

    if letter is None:
        print("No letters found")
        time.sleep(PRINT_DELAY)
        continue

    # chatgot to prevent immediate duplicate prints
    if letter["id"] == last_printed_id:
        print("Skipping duplicate letter")
        time.sleep(PRINT_DELAY)
        continue

    last_printed_id = letter["id"]

    print(f"Printing {source} letter:", letter["id"])

    content = letter.get("content", "")
    author = letter.get("author", "Anonymous")

    text = format_letter(content, author)

    printer.write(text.encode("ascii", errors="ignore"))
    
    time.sleep(0.5)

#after printing update backend and console
    if source == "visitor":

        mark_visitor_printed(letter["id"])

    elif source == "archive":

        current = letter.get("printed_count", 0)

        increment_archive_print(
            letter["id"],
            current
        )

    time.sleep(PRINT_DELAY)