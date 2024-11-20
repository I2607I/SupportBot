from project.tasks.celery_app import app
from project.ml.SupportBot import SupportBot

support_bot = SupportBot()


@app.task
def mock_ml_request(message, history):
    try:
        answer, score, history = support_bot.qa(message, history[-9000:])
    except:
        support_bot.update_model()
        answer, score, history = support_bot.qa(message, history[-9000:])
    return answer, score, history
