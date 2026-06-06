import re

def total_uber(purchases):
    uber_pattern = re.compile(r"uber", re.IGNORECASE)
    sum_uber = 0.0
    uber_occurrences = 0
    for purchase in purchases:
        if uber_pattern.match(purchase.description):
            uber_occurrences += 1
            sum_uber += float(purchase.value.replace(',', '.'))
    print("total uber({0}): R${1}".format(str(uber_occurrences), str(round(sum_uber, 2))))


def seller_total(purchases: list, seller_name: str):
    seller_pattern = re.compile(seller_name.lower(), re.IGNORECASE)
    seller_sum = 0.0
    seller_occurrences = 0
    for purchase in purchases:
        if seller_pattern.match(purchase.description.lower()):
            seller_occurrences += 1
            seller_sum += float(purchase.value.replace(',', '.'))
    print("total {2}({0}): R${1}".format(str(seller_occurrences), str(round(seller_sum, 2)), seller_name))


def add_uber_tag(purchase_obj_list: list):
    for purchase in purchase_obj_list:
        if 'uber' not in purchase.description.lower():
            pass
        elif 'uber' not in purchase.tags:
            purchase.tags.append('uber')


def add_ifood_tag(purchase_obj_list: list):
    for purchase in purchase_obj_list:
        if not (('ifood' in purchase.description.lower()) or ('ifd*' in purchase.description.lower())):
            pass
        elif 'ifood' not in purchase.tags:
            purchase.tags.append('ifood')
            purchase.tags.append('food')    

def total_by_tag(purchase_obj_list: list, tag: str):
    tag_occurrences = 0
    value_sum = 0
    for purchase in purchase_obj_list:
        if tag in purchase.tags:
            tag_occurrences += 1
            value_sum += float(purchase.value.replace(',', '.'))
    print("total tag - {2} - ({0}): R${1}".format(str(tag_occurrences), str(round(value_sum, 2)), tag))
    return value_sum


def total_without_tag(purchase_obj_list: list):
    tag_occurrences = 0
    value_sum = 0
    for purchase in purchase_obj_list:
        if not purchase.tags:
            tag_occurrences += 1
            value = purchase.value.replace(',', '.')
            value_sum += float(value.replace('R$ ', ''))
    print("total no tag ({0}): R${1}".format(str(tag_occurrences), str(round(value_sum, 2))))
    return value_sum


def purchases_without_tag(purchase_obj_list: list):
    ret_list = []
    for purchase in purchase_obj_list:
        if not purchase.tags:
            ret_list.append(purchase)
    return ret_list


def add_related_tag(purchase_obj_list: list, ref_tag: str, new_add: str):
    for purchase in purchase_obj_list:
        if ref_tag.lower() not in purchase.tags:
            pass
        elif new_add.lower() not in purchase.tags:
            purchase.tags.append(new_add.lower())


def add_tag_based_on_description(purchase_obj_list: list, description, tag_to_add):
    for purchase in purchase_obj_list:
        if description.lower() not in purchase.description.lower():
            pass
        elif tag_to_add.lower() not in purchase.tags:
            purchase.tags.append(tag_to_add.lower())            