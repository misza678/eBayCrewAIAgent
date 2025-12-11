import sys
import signal

def patch_windows_signals():
    """
    Naprawia brakujące sygnały Unixowe na Windowsie dla biblioteki CrewAI.
    Musi być uruchomione PRZED jakimkolwiek importem crewai.
    """
    if sys.platform.startswith('win'):
        # Lista sygnałów, których CrewAI szuka, a Windows ich nie ma
        missing_signals = [
            'SIGHUP', 'SIGTSTP', 'SIGCONT', 'SIGQUIT', 'SIGTRAP', 'SIGUSR1', 'SIGUSR2'
        ]
        
        for sig_name in missing_signals:
            if not hasattr(signal, sig_name):
                # Przypisujemy sztuczną wartość (np. 1), żeby biblioteka się nie wywaliła
                setattr(signal, sig_name, 1)

# Uruchamiamy to natychmiast przy imporcie tego pliku
patch_windows_signals()