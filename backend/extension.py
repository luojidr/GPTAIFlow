from kafka import KafkaProducer, KafkaConsumer
import config
import pickle

kafka_producer = KafkaProducer(
    bootstrap_servers=config.KAFKA_SERVER,
    value_serializer=lambda m: pickle.dumps(m),
    security_protocol=config.KAFKA_SECURITY_PROTOCOL,
    sasl_mechanism=config.KAFKA_SASL_MECHANISM,
    sasl_plain_username=config.KAFKA_USERNAME,
    sasl_plain_password=config.KAFKA_PASSWORD
)

topic_list = [config.KAFKA_DEFAULT_TOPIC] + \
             config.KAFKA_OPENAI_TOPIC_FUNCTION + \
             config.KAFKA_UNIQ_TOPIC_FUNCTION + \
             [config.KAFKA_MONITOR_TOPIC]

kafka_consumer_list = []
assert config.WORKER_THREAD_NUM > len(topic_list)

for i in range(config.WORKER_THREAD_NUM):
    kafka_consumer = KafkaConsumer(
        bootstrap_servers=config.KAFKA_SERVER,
        group_id=config.KAFKA_GROUP_ID,
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        value_deserializer = lambda m: pickle.loads(m),
        security_protocol=config.KAFKA_SECURITY_PROTOCOL,
        sasl_mechanism=config.KAFKA_SASL_MECHANISM,
        sasl_plain_username=config.KAFKA_USERNAME,
        sasl_plain_password=config.KAFKA_PASSWORD,
        max_poll_interval_ms=1200000,
        session_timeout_ms=30000
    )
    kafka_consumer.subscribe([topic_list[i % len(topic_list)]])
    kafka_consumer_list.append(kafka_consumer)
                               
