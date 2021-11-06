from google.cloud import pubsub, pubsub_v1
publisher = pubsub_v1.PublisherClient()

topic_path = publisher.topic_path("sampleprojects-234502", "converter")


with pubsub.SubscriberClient() as subscriber:
    sub_path = subscriber.subscription_path("sampleprojects-234502", "converter-sub")
    response = subscriber.pull(
        request={
            "subscription": sub_path,
            "max_messages": 5,
        }
    )
    for msg in response.received_messages:
        print("Received message:", msg.message.data)