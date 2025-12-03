from sqlalchemy.orm import Session
from datetime import datetime

from app import models
from app.utils.sanitizer import sanitize_input
from app.utils.llm_client import call_llm  # wrapper for model calls

def answer_question(user_id: int | None, question: str, db: Session) -> dict:
    question = sanitize_input(question)
    if len(question) < 3:
        return {"answer": "Please ask a more specific question.", "source": "SYSTEM", "kb_id": None}

    kb_results = db.query(models.KBEntry).filter(models.KBEntry.question.ilike(f"%{question}%")).order_by(models.KBEntry.rating.desc()).all()
    if kb_results:
        best = kb_results[0]
        # log usage
        usage = models.KBUsageLog(kb_id=best.id, user_id=user_id, question=question, timestamp=datetime.utcnow())
        db.add(usage)
        db.commit()
        return {"answer": best.answer, "source": "KNOWLEDGE_BASE", "kb_id": best.id, "author": best.author_id, "requestRating": True}

    # fallback to LLM
    try:
        context = "Restaurant context..."  # build from DB if desired
        prompt = f"You are a helpful restaurant assistant.\nContext: {context}\nQuestion: {question}\nAnswer:"
        llm_response = call_llm(model="llama2", prompt=prompt, max_tokens=200)

        llm_log = models.LLMUsageLog(user_id=user_id, question=question, response=llm_response, timestamp=datetime.utcnow())
        db.add(llm_log)
        db.commit()

        return {"answer": llm_response, "source": "LLM", "kb_id": None, "requestRating": False}
    except Exception:
        return {"answer": "I'm having trouble answering right now. Please contact our manager for assistance.", "source": "ERROR", "kb_id": None}


def rate_kb_answer(user_id: int, kb_id: int, rating: int, db: Session) -> bool:
    if rating < 0 or rating > 5:
        raise ValueError("Invalid rating")
    kb = db.query(models.KBEntry).get(kb_id)
    if not kb:
        raise ValueError("KB entry not found")

    with db.begin():
        kb_rating = models.KBRating(kb_id=kb_id, user_id=user_id, rating=rating, timestamp=datetime.utcnow())
        db.add(kb_rating)

        all_ratings = db.query(models.KBRating).filter(models.KBRating.kb_id == kb_id).all()
        avg = sum(r.rating for r in all_ratings) / len(all_ratings)
        kb.rating = avg
        kb.rating_count = len(all_ratings)
        if rating == 0:
            kb.flagged = True
            notify_manager(f"KB entry #{kb_id} flagged for review (rating: 0)")

    return True


def review_flagged_content(kb_id: int, manager_id: int, action: str, reason: str, db: Session) -> bool:
    manager = db.query(models.User).get(manager_id)
    if manager is None or manager.user_type != "MANAGER":
        raise ValueError("Unauthorized")

    kb = db.query(models.KBEntry).get(kb_id)
    if kb is None or not kb.flagged:
        raise ValueError("Invalid KB entry or not flagged")

    with db.begin():
        if action == "REMOVE":
            author_id = kb.author_id
            db.delete(kb)
            author = db.query(models.User).get(author_id)
            if author:
                author.kb_contributor = False
                notify_user(author_id, f"Your KB entry was removed: {reason}")
        else:
            kb.flagged = False
            kb.reviewed_by = manager_id
            kb.review_note = reason
            kb.reviewed_at = datetime.utcnow()
            db.add(kb)

    return True
