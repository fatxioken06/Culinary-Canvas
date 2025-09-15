import logging
import redis

logger = logging.getLogger("django")


class RedisHelper:
    def __init__(self):
        self.redis_client = redis.Redis(
            host="localhost", port=6379, db=0, decode_responses=True
        )

    def set_email_verification_code(self, user_id, code, expiry=120):
        """Email verify kodini saqlash (2 daqiqa default)"""
        try:
            key = f"email_verify:{user_id}"
            self.redis_client.setex(key, expiry, code)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e!s}")
            return False

    def get_email_verification_code(self, user_id):
        """Email verify kodini olish"""
        try:
            key = f"email_verify:{user_id}"
            code = self.redis_client.get(key)
            if code:
                self.redis_client.delete(key)  # Kod ishlatilgandan keyin o'chirish
                return code
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e!s}")
            return None
