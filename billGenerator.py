from PIL import Image, ImageDraw, ImageFont
import os
from num2words import num2words
import textwrap


# Get the current working directory
cwd = os.getcwd()
TEMPLATES = os.path.join(cwd, 'Templates')
STATIC = os.path.join(cwd, 'Static')

# Get Fonts
lato_black_35 = ImageFont.truetype(os.path.join(STATIC, 'Fonts', 'Lato', 'Lato-Black.ttf'), 35)
lato_black_28 = ImageFont.truetype(os.path.join(STATIC, 'Fonts', 'Lato', 'Lato-Black.ttf'), 28)

# Colors
red = '#c20101'
grey = '#747474'



# Custom mapping of numbers to Indian monetary words
indian_monetary_words = {
        0: 'Zero',
        1: 'One',
        2: 'Two',
        3: 'Three',
        4: 'Four',
        5: 'Five',
        6: 'Six',
        7: 'Seven',
        8: 'Eight',
        9: 'Nine',
        10: 'Ten',
        11: 'Eleven',
        12: 'Twelve',
        13: 'Thirteen',
        14: 'Fourteen',
        15: 'Fifteen',
        16: 'Sixteen',
        17: 'Seventeen',
        18: 'Eighteen',
        19: 'Nineteen',
        20: 'Twenty',
        30: 'Thirty',
        40: 'Forty',
        50: 'Fifty',
        60: 'Sixty',
        70: 'Seventy',
        80: 'Eighty',
        90: 'Ninety',
        100: 'Hundred',
        1000: 'Thousand',
        100000: 'Lakh',
        10000000: 'Crore'
    }

def convert_to_indian_monetary_words(number):
    # Convert the float value to words using num2words
    words = num2words(number, lang='en_IN')
    # Split the words into individual parts
    parts = words.split()
    # Iterate through the parts and replace the numbers with Indian monetary words
    for i in range(len(parts)):
        try:
            num = int(parts[i])
            if num in indian_monetary_words:
                parts[i] = indian_monetary_words[num]
        except ValueError:
            pass
    # Join the parts back into a single string
    result = ' '.join(parts)
    return result

def convert_to_indian_monetary_words(number):
    # Convert the float value to words using num2words
    words = num2words(number, lang='en_IN')
    # Split the words into individual parts
    parts = words.split()
    # Iterate through the parts and replace the numbers with Indian monetary words
    for i in range(len(parts)):
        try:
            num = int(parts[i])
            if num in indian_monetary_words:
                parts[i] = indian_monetary_words[num]
        except ValueError:
            pass
    # Join the parts back into a single string
    result = ' '.join(parts)
    return result

def generate_bill(bill_data, path_to_template):
    # Open the template
    invoice = Image.open(path_to_template)
    # Get the draw object
    draw = ImageDraw.Draw(invoice)
    # Draw the text
    draw.text((260, 552), bill_data['invoice_no'], fill=red, font=lato_black_35)

    if bill_data.get('e_way_no',None):
        draw.text((285, 632), bill_data['e_way_no'], fill=grey, font=lato_black_28)

    draw.text((165, 673), bill_data['date'], fill=grey, font=lato_black_28)
    draw.text((800, 140), bill_data['party_details']['name'], fill=grey, font=lato_black_28)
    draw.text((800, 200), wrap(bill_data['party_details']['street_address'], 40)[0], fill=grey, font=lato_black_28)
    draw.text((845, 470), bill_data['party_details']['state'], fill=grey, font=lato_black_28)
    draw.text((1270, 470), bill_data['party_details']['state_code'], fill=grey, font=lato_black_28)
    draw.text((965, 552), bill_data['party_details']['gst_no'], fill=grey, font=lato_black_35)
    if bill_data.get('hsn_code',None):
        draw.text((1010, 645), bill_data['hsn_code'], fill=grey, font=lato_black_35)
    elif bill_data.get('sac_code',None):
        draw.text((1010, 645), bill_data['sac_code'], fill=grey, font=lato_black_35)
    
    base = 800
    for n,item in enumerate(bill_data['items']):
        particulars,lines = wrap(item[0], 35)
        draw.text((55, base), str(n+1), fill=grey, font=lato_black_35)
        draw.text((100, base), particulars, fill=grey, font=lato_black_35)

        _, _, w, h = draw.textbbox((720, base), item[1], font=lato_black_35)
        draw.text(((920 - w)/2+720,base), item[1], fill=grey, font=lato_black_35)

        _, _, w, h = draw.textbbox((920, base), item[2], font=lato_black_35)       
        draw.text(((1150 - w)/2+920, base), item[2], fill=grey, font=lato_black_35)

        _, _, w, h = draw.textbbox((1150, base), item[3], font=lato_black_35)       
        draw.text(((1350 - w)/2+1150, base), item[3], fill=grey, font=lato_black_35)
        base = base + (lines * 40) + 60
    
    if bill_data.get('others_amt',None):
        _, _, w, h = draw.textbbox((1150, base), bill_data['others_amt'], font=lato_black_35)       
        draw.text(((1350 - w)/2+1150, 1480), bill_data['others_amt'], fill=grey, font=lato_black_35)

    _, _, w, h = draw.textbbox((1150, base), bill_data['taxable_value'], font=lato_black_35)
    draw.text(((1350 - w)/2+1150, 1545), bill_data['taxable_value'], fill=grey, font=lato_black_35)

    _, _, w, h = draw.textbbox((1150, base), bill_data['cgst'], font=lato_black_35)
    draw.text(((1350 - w)/2+1150, 1605), bill_data['cgst'], fill=grey, font=lato_black_35)

    _, _, w, h = draw.textbbox((1150, base), bill_data['sgst'], font=lato_black_35)
    draw.text(((1350 - w)/2+1150, 1662), bill_data['sgst'], fill=grey, font=lato_black_35)

    _, _, w, h = draw.textbbox((1150, base), bill_data['igst'], font=lato_black_35)
    draw.text(((1350 - w)/2+1150, 1720), bill_data['igst'], fill=grey, font=lato_black_35)

    _, _, w, h = draw.textbbox((1150, base), bill_data['grand_total'], font=lato_black_35)
    draw.text(((1350 - w)/2+1150, 1772), bill_data['grand_total'], fill=grey, font=lato_black_35)

    total_in_words = convert_to_indian_monetary_words(float(bill_data['grand_total'])).upper()
    total_in_words = wrap(total_in_words + " RUPPEES ONLY",40)[0]
    draw.text((55, 1620), total_in_words, fill=grey, font=lato_black_35)

    return invoice


def wrap(text,width):
    wrapper = textwrap.TextWrapper(width=width)
    word_list = wrapper.wrap(text=text)
    text_new = ''
    lines = 0
    for ii in word_list[:-1]:
       text_new = text_new + ii + '\n'
       lines += 1
    text_new += word_list[-1]
    return [text_new,lines]
