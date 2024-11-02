from django.core.cache import cache
from django.utils.timezone import now
import threading
import time


class CacheMonitor:
    @staticmethod
    def log_cache_status(key='demo_stats_data'):
        """Logga lo stato della cache"""
        data = cache.get(key)
        if data:
            timestamp = data.get('cache_timestamp', now())
            age = now() - timestamp
            minutes = age.total_seconds() / 60
            print(f"\n✅ CACHE HIT - Dati trovati in cache")
            print(f"⏰ Età dei dati: {minutes:.2f} minuti")
            print(f"📊 Dati disponibili: {len(data)} elementi")
            return True
        print("\n❌ CACHE MISS - Dati non trovati in cache")
        print("🔄 Esecuzione query per generare nuovi dati...")
        return False

    @classmethod
    def start_monitoring(cls, interval=300):
        """Avvia il monitoraggio periodico della cache"""
        def monitor_loop():
            while True:
                print("\n=== Controllo periodico cache ===")
                cls.log_cache_status()
                time.sleep(interval)

        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
