from config.default import *
from dotenv import load_dotenv

load_dotenv(os.path.join(BASE_DIR, '.env'))

SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://{user}:{pw}@{url}/{db}'.format(
    user=os.getenv('DB_USER'),
    pw=os.getenv('DB_PASSWORD'),
    url=os.getenv('DB_HOST'),
    db=os.getenv('DB_NAME'),
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = b'\xd5|U\xa7\xe8X\x07\xd1\x98\xf5w\x8c\xda\xb7p4'