""" File containing the function to build the correct mappings for each mixer message """

import re
import copy


def build_mappings(mixer):
    """Build the mappings"""
    # Takes in a mixer object and builds the mappings for the mixer
    # returns a dictionary of mappings

    mappings = {}
    secondary_mappings = {}
    reverse_mappings = {}  # Used to detect duplicate mappings
    addresses = mixer.addresses_to_load + mixer.extra_addresses_to_load
    for address_row in addresses:
        (new_mappings, new_secondary_mappings, remove_mappings) = expand_address(
            mixer, address_row, reverse_mappings
        )
        mappings.update(new_mappings)
        for remove_mapping in remove_mappings:
            del mappings[remove_mapping]
        secondary_mappings.update(new_secondary_mappings)
    return mappings, secondary_mappings


def expand_address(mixer, address_tuple, reverse_mappings):
    """Expand an address including wildcards"""
    mappings = {}
    secondary_mappings = {}
    processlist = [address_tuple]
    remove_mappings = []
    while processlist:
        row = processlist.pop(-1)
        if mixer.include and row.get("tag") and row.get("tag") not in mixer.include:
            continue
        input = row.get("input")
        output = row.get("output") or input
        matches = re.search(r"\{(.*?)\}", input)
        if matches:
            match_var = matches.group(1)
            input_start_index = get_starting_index(mixer, row, match_var, False)
            output_start_index = get_starting_index(mixer, row, match_var, True)
            input_zfill_num = get_padding_num(mixer, row, match_var, False)
            output_zfill_num = get_padding_num(mixer, row, match_var, True)
            max_count = getattr(mixer, match_var)
            for number in range(input_start_index, max_count + input_start_index):
                new_row = copy.deepcopy(row)
                # Loop through the template how every many times there are
                # items and build the specific keys needed
                # building one address for what the mixer expects and another
                # about what we want internally

                input_build = input.replace(
                    "{" + match_var + "}",
                    str(number).zfill(input_zfill_num),
                )
                output_number = number + (output_start_index - input_start_index)
                output_build = output.replace(
                    "{" + match_var + "}",
                    str(output_number).zfill(output_zfill_num),
                )
                new_row["input"] = input_build
                new_row["output"] = output_build
                processlist.append(
                    new_row
                )  # add to the list to check if there are any other match variables
        else:
            # No match variables so just add the address to the list
            if "secondary_output" in row:
                for suffix in row["secondary_output"].keys():
                    address = row["output"] + suffix
                    secondary_mappings[address] = row["input"]
            mappings[input] = row
            if row["output"] in reverse_mappings:
                remove_mappings.append(reverse_mappings[row["output"]])
            reverse_mappings[row["output"]] = row["input"]
    return mappings, secondary_mappings, remove_mappings


def get_padding_num(mixer, row, field_type: str, output=False):
    """Get the number of digits to pad for a given field"""
    default_padding_output = 0
    zfill_num = 0
    if output:
        if "output_padding" in row and field_type in row["output_padding"]:
            zfill_num = row["output_padding"][field_type]
        else:
            zfill_num = default_padding_output
    else:
        if "input_padding" in row and field_type in row["input_padding"]:
            zfill_num = row["input_padding"][field_type]
        else:
            # What is the maxiumum number for this type of thing then
            # calculate number of digits needed
            max_count = getattr(mixer, field_type)
            zfill_num = len(str(max_count))
    return zfill_num


def get_starting_index(mixer, row, field_type: str, output=False):
    """Get the starting index for a set of numbers"""
    starting_index = 1
    if output:
        if "output_indexing" in row and field_type in row["output_indexing"]:
            starting_index = row["output_indexing"][field_type]
    else:
        if "input_indexing" in row and field_type in row["input_indexing"]:
            starting_index = row["input_indexing"][field_type]
    return starting_index
