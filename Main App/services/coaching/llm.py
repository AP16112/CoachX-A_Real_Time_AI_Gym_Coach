# Here in this file, we are defining a class called LLMCoach that interacts with a large language model (LLM) to provide feedback on workout form. The class is initialized with a Groq client, which is used to send requests to the LLM. It maintains a history of interactions and uses a system prompt to guide the model's responses. The give_feedback method constructs a prompt based on the workout event and any identified form issues, sends it to the LLM, and returns the generated feedback while also updating the interaction history.


from services.config.workout_config import PROMPT


class LLMCoach:
    # Here groq_client is an instance of the Groq client that allows us to communicate with the LLM. The history list keeps track of the last 10 interactions with the model, which helps maintain context for generating more relevant feedback. The system_prompt is a predefined instruction that guides the model on how to respond to user events and form issues during workouts.
    def __init__(self, groq_client):
        self.client = groq_client    # The Groq client is used to send requests to the LLM for generating feedback based on workout events and form issues.
        self.history = []
        self.system_prompt = PROMPT


    # This method takes an event (like 'workout_started', 'set_completed', etc.) and an optional issue (like 'back arching', 'knee misalignment', etc.) as input. It constructs a prompt for the LLM, sends it to the model, and retrieves the generated feedback. The feedback is then appended to the history for context in future interactions.
    # e.g Events :- Start Workout, Set Completed, End Workout, etc
    # e.g Issues :- Threw Metrics Issue arrise, Back Arching, Knee Misalignment, Shoulder Position, etc
    def give_feedback(self, event, issue):
        prompt = f"Event: {event}"

        # If a specific form issue is detected, we append it to the prompt so that the LLM can provide targeted feedback. This allows the model to generate advice that addresses the user's current form problems during their workout session.
        if issue:
            prompt += f" Form Issue: {issue}"

        # We construct the messages to send to the LLM. The system message provides context and instructions, the last 10 messages from history maintain conversational context, and the user message contains the current prompt. This structure helps the LLM understand the ongoing conversation and generate relevant feedback.
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.history[-10:],    # We include the last 10 messages from history to maintain context for the LLM. This helps the model understand the flow of the conversation and provide more coherent feedback based on previous interactions.
            # Here * is used to unpack the last 10 messages from the history list and include them in the messages list. This ensures that the LLM has access to recent interactions, which can improve the relevance and accuracy of its responses.
            # If we don't use this *, the LLM will not have context of the previous messages and will treat each prompt as a standalone request, which may lead to less coherent or relevant feedback.
            {"role": "user", "content": prompt}
        ]

        # We send the constructed messages to the LLM using the Groq client. The model processes the input and generates a response based on the provided context and instructions. The temperature parameter controls the randomness of the output, with lower values producing more deterministic responses.
        # Here this self.client.chat.completions.create() method sends the messages to the LLM and retrieves the generated feedback. The response is then processed to extract the content, which is returned as the feedback for the user.
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.4,   # The temperature parameter controls the randomness of the LLM's output. A lower value (like 0.4) makes the responses more focused and deterministic, while a higher value would introduce more variability and creativity in the feedback.
        )

        # We extract the content of the LLM's response and append it to the history for future context. This allows the model to maintain a coherent conversation with the user, providing feedback that builds on previous interactions.
        text = response.choices[0].message.content.strip()

        # We append the LLM's response to the history list, which keeps track of the last 10 interactions. This is important for maintaining context in future feedback requests, allowing the model to provide more relevant and coherent advice based on previous events and form issues.
        self.history.append({"role": "assistant", "content": text})

        return text
    

    