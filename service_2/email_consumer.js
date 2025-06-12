const {decryptData} = require("./decrypt_data");
const { Kafka } = require('kafkajs');
const {email_event_mapper} = require("./event_mapper");

const kafka = new Kafka({
  brokers: ['172.23.247.236:9092']
})

const consumer = kafka.consumer(
  {
  groupId: 'test-consumer-group-2',
  sessionTimeout: 30000,
  heartbeatInterval: 5000,
  maxPollInterval: 100000,
  }
);


async function runEmailConsumer() {
  await consumer.connect();
  await consumer.subscribe({ topic: 'email_event', fromBeginning: true });
  await consumer.run({
    autoCommit: true,
    eachMessage: async ({topic, message}) => {
      console.log(`THIS IS THE TOPIC: ${topic}`);
      //console.log(`THIS IS THE MESSAGE: ${message.value}`);
      new Promise((resolve, reject) => {
        try {
          data = decryptData(message.value);
          resolve(data);
        } catch (error) {
          reject(error);
        }
      }).then(data => {
        console.log("Decrypted data:", data);
        email_event_mapper(data);
      }).catch(error => {
        console.error("Error decrypting message:", error);
      })
    }
  });
}

process.on('SIGINT', async () => {
  console.log('SIGINT received, disconnecting consumer...');
  await consumer.disconnect();
  process.exit(0);
});

module.exports = {runEmailConsumer};