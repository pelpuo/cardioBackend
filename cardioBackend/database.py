import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://panda:pandaSage@cardio-db.hquh868.mongodb.net/?retryWrites=true&w=majority')

db = client.cardioDatabase