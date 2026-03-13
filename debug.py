import pyttsx3
engine = pyttsx3.init()
engine.setProperty("rate", 165)
engine.say("Hello, this is a test")
engine.runAndWait()
print("Done")