def process_audio_to_openai_training_format(original_list):
    """
    Processes a list of dictionaries into a format suitable for training with OpenAI.
    Each dictionary in the input list is expected to have 'text' and 'speaker' keys.
    The function unifies consecutive dictionaries with the same 'speaker' value,
    merging their 'text' values into a single string, separated by spaces.
    It also transforms 'speaker' into 'role', determining the most frequent speaker
    as 'assistant' and the less frequent as 'user'.

    Parameters:
    original_list (list): A list of dictionaries, each containing 'text' and 'speaker' keys.

    Returns:
    list: A list of unified dictionaries with 'content' and 'role' keys.
    """

    # Filter the list to retain only 'text' and 'speaker' keys from each dictionary
    filtered_list = [{'text': dic['text'], 'speaker': dic['speaker']} for dic in original_list]

    # Count the frequency of each 'speaker' value
    speaker_frequency = {}
    for dic in filtered_list:
        if dic['speaker'] in speaker_frequency:
            speaker_frequency[dic['speaker']] += 1
        else:
            speaker_frequency[dic['speaker']] = 1

    # Determine the most and least frequent 'speaker'
    most_frequent_speaker = max(speaker_frequency, key=speaker_frequency.get)
    least_frequent_speaker = min(speaker_frequency, key=speaker_frequency.get)

    # Format the list with new keys and values
    formatted_list = [
        {'content': dic['text'], 'role': 'assistant' if dic['speaker'] == most_frequent_speaker else 'user'}
        for dic in filtered_list
    ]

    # List to store the unified result
    unified_list = []

    # Temporary variable to hold the current dictionary while iterating
    temp_dic = None

    # Iterate over each dictionary in the formatted list
    for dic in formatted_list:
        # If there's no temporary dictionary, it's the start of a potential sequence
        if not temp_dic:
            temp_dic = dic
        else:
            # If the 'role' of the current dictionary matches the temporary one,
            # their contents are unified.
            if dic['role'] == temp_dic['role']:
                temp_dic['content'] += " " + dic['content']
            else:
                # If the 'role' is different, add the temporary dictionary to the unified list
                # and start a new temporary dictionary with the current one
                unified_list.append(temp_dic)
                temp_dic = dic

    # Add the last temporary dictionary to the unified list
    if temp_dic:
        unified_list.append(temp_dic)

    # Return the result
    return unified_list


# Example Usage
# if __name__ == "__main__":
