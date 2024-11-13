import logging

import numpy as np

from scoring.common import EVALUATION_DATASET_SAMPLE_SIZE, MAX_GENERATION_LENGTH, MAX_SEQ_LEN
from scoring.dataset import StreamedSyntheticDataset
from scoring.scoring_logic.logic import scoring_workflow


def load_dataset():

    print("Sampling dataset")
    try:
        dataset = StreamedSyntheticDataset(
            max_input_len=MAX_SEQ_LEN - MAX_GENERATION_LENGTH - 200,
            mock=True,
        )
        sampled_data = dataset.sample_dataset(EVALUATION_DATASET_SAMPLE_SIZE, dummy=True)
        """
        shape of sampled_data: a list structured like the following:
        [
                (
                    # target text
                    "I understand your concern about the project timeline. Let me assure you that we'll meet our deadlines by prioritizing key deliverables and maintaining clear communication throughout the process.",
                    # last user message
                    "I'm worried we won't finish the project on time. What can we do?",
                    # voice_description
                    "Eric's voice is deep and resonant, providing a commanding presence in his speech. A **male voice with an American accent**, his **very low-pitched voice** is captured with crisp clarity. His tone is **authoritative yet slightly monotone**, emphasizing his strong and steady delivery."
                ),
                (
                    "The latest market analysis shows promising growth opportunities in the Asia-Pacific region. Our data indicates a 15% increase in consumer demand for our products.",
                    "What are the key findings from the market research?",
                    "Laura's voice is warm and friendly, conveying messages with clarity and enthusiasm. A **female voice with an American accent** enunciates every word with precision. Her voice is **very close-sounding**, and the recording is excellent, capturing her **slightly high-pitched voice** with crisp clarity. Her tone is **very expressive and animated**, bringing energy to her delivery."
                ),
                (
                    "To improve your Python code performance, consider using list comprehensions instead of loops, leverage built-in functions, and implement proper data structures.",
                    "How can I make my Python code run faster?",
                    "Patrick's voice is authoritative and assertive, perfect for informative and instructional content. A **male voice with an American accent** enunciates every word with precision. His voice is **very close-sounding**, and the recording is excellent, capturing his **fairly low-pitched voice** with crisp clarity. His tone is **slightly monotone**, emphasizing clarity and directness."
                )
            ]
        """
        return sampled_data
    except Exception as e:
        failure_reason = str(e)
        raise Exception(f"Error loading dataset: {failure_reason}")


def apply_weights(base_score: float, text: str, weights: dict) -> float:
    """
    Apply multiple weighting mechanisms to adjust the base score.

    :param base_score: The initial score before weighting.
    :param text: The text input used to calculate length-based weights.
    :param weights: A dictionary of weights to apply.
    :return: Weighted score.
    """
    weighted_score = base_score
    # An Example scaffold for when we choose to leverage weights

    # if isinstance(weights, dict) and "text_length" in weights:
    #     length_factor = len(text) / 100  # Normalize text length by dividing by 100
    #     weighted_score *= weights["text_length"] * length_factor

    # Example to add other weights
    # # Apply voice description weight if provided
    # if "voice_description" in weights:
    #     description_factor = len(voice_description) / 50  # Normalize by dividing by 50 as an example
    #     weighted_score *= weights["voice_description"] * description_factor

    return weighted_score


def get_tts_score(request: str) -> dict:
    """
    Calculate and return the TTS scores with optional weighting.

    :param request: The request object containing necessary details for scoring.
    :return: A dictionary with the final score and any errors.
    """

    # Load the dataset containing input data for scoring.
    data = load_dataset()
    # Initialize an empty list to store scores for each processed text.
    scores = []
    # Initialize the result dictionary with a default final score of 0.
    result = {"final_score": 0}
    # Define the weights for scoring, with 'text_length' having a default weight of 1.
    weights = {"text_length": 1}

    # Iterate over the data, which contains tuples of text, last user message, and voice description.
    for text, last_user_message, voice_description in data:
        try:
            # Calculate the base score using the scoring workflow function.
            base_score = scoring_workflow(request.repo_namespace, request.repo_name, text, voice_description)

            # Extract float values from each tensor in the 'scores' list for further processing
            float_values_from_tensors = [score.item() for score in base_score]

            # Apply weights to the base score based on text properties.
            weighted_score = apply_weights(float_values_from_tensors, text, weights)

            # Append the weighted score to the scores list.
            scores.append(weighted_score)

        # Catch any exceptions that occur during score calculation.
        except Exception as e:
            # Log the error and update the result dictionary with the error message.
            logging.info(f"Error calculating score: {e}")
            result["error"] = str(e)

    # Calculate the average score after the loop completes.
    if scores:
        mean_value = float(np.mean(scores))
        clipped_mean_value = np.clip(mean_value, 0, 1) # Clip value between 0 and 1
        result["final_score"] = clipped_mean_value

    # Return the final result dictionary containing the score and any errors.
    return result
