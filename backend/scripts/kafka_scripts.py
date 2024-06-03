from kafka import KafkaConsumer, TopicPartition
import pickle
# Kafka配置
topic_names  = ['common',"dall_e","open_ai","webpilot"]
for topic_name in topic_names:
    consumer_group = 'fgg'
    consumer = KafkaConsumer(bootstrap_servers="192.168.191.200",
                                    group_id="hc_group",
                                    auto_offset_reset='earliest',
                                    enable_auto_commit=False,
                                    value_deserializer = lambda m: pickle.loads(m),
                                    security_protocol="SASL_PLAINTEXT",
                                    sasl_mechanism="PLAIN",
                                    sasl_plain_username="hc",
                                    sasl_plain_password="hcpwd",
                                    max_poll_interval_ms=1200000,
                                    session_timeout_ms=30000)

    partitions = consumer.partitions_for_topic("common")
    if partitions:
        print(f"Topic '{topic_name}' has {len(partitions)} partitions.")
    else:
        print(f"Topic '{topic_name}' not found.")
    consumer.subscribe([topic_name])
    partitions = consumer.partitions_for_topic(topic_name)
    topic_partitions = [TopicPartition(topic_name, p) for p in partitions]
    end_offsets = consumer.end_offsets(topic_partitions)
    for tp in topic_partitions:
        consumer_offset = consumer.committed(tp)
        end_offset = end_offsets[tp]
        print(f"Partition: {tp.partition}, Consumer Offset: {consumer_offset}, End Offset: {end_offset}, Unconsumed Messages: {end_offset - consumer_offset}")
    consumer.close()

