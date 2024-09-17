# Dataset Overview

## 1. Counselchat.com Dataset

**Overview:**  

The Counselchat.com dataset is derived from an expert community where verified therapists respond to user-submitted mental health questions. This platform allows licensed mental health professionals to provide guidance and build their reputations, making the data highly credible. The dataset contains both scraped and officially provided data from the platform.

**Key Information:**

- **Source:** Scraped from Counselchat.com, with data provided by the platform’s founders.
- **Content:**  
  - 31 topics (e.g., "depression," "anxiety," "military issues")
  - 307 verified therapists, primarily located on the US West Coast
  - Over 300 responses per topic in some cases
- **Therapists' Qualifications:** Includes licensed professionals like Ph.D. psychologists, social workers, and mental health counselors.
- **Format:** CSV with 10 columns:
  - `questionID` (unique identifier)
  - `questionTitle` (title of the user’s question)
  - `questionText` (body of the question)
  - `questionLink` (URL to the question)
  - `topic` (mental health topic)
  - `therapistInfo` (therapist’s details)
  - `therapistURL` (therapist’s profile link)
  - `answerText` (therapist’s response)
  - `upvotes` (number of upvotes for the response)
  - `split` (for training, validation, and testing)

**Observations:**  

The dataset is highly useful for training language models (LLMs) for mental health-related tasks, providing expert responses for analysis and prediction models. The data ensures that all advice comes from licensed professionals, improving reliability over crowdsourced alternatives.

[See here for Counselchat.com article](https://towardsdatascience.com/counsel-chat-bootstrapping-high-quality-therapy-data-971b419f33da)

## 2. Mental Health Dataset

**Overview:**  

This dataset is designed for building AI-driven chatbots and virtual assistants that interact with users on mental health topics. It provides a range of user inputs and corresponding responses to facilitate the detection of various mental health conditions and user intents.

**Key Information:**

- **Primary Purpose:** To train models that can understand and respond to user inputs related to mental health, and casual conversations.
- **Categories:** Includes diverse patterns such as greetings, emotional states, questions, and mental health-related expressions. Examples include:
  - 'greeting,' 'morning,' 'depressed,' 'anxious,' 'suicide,' 'help,' 'casual,' 'happy,' 'stressed,' 'meditation,' and 'mental-health-fact.'
  - Over 30 mental health-related facts and topics.
- **Format:** Structured as user input patterns and predefined responses to train natural language processing (NLP) models.
- **Use Cases:** Ideal for training AI/ML models for virtual health assistants, chatbots, and conversational AI systems that support mental health.

[See here for Mental Health Dataset on Kaggle](https://www.kaggle.com/datasets/jiscecseaiml/mental-health-dataset?resource=download)

