import random


# def get_score(store, phone, email, birthday=None, gender=None, first_name=None, last_name=None):
def get_score(store,online_score_req):
    score = 0
    if online_score_req.phone:
        score += 1.5
    if online_score_req.email:
        score += 1.5
    if online_score_req.birthday and online_score_req.gender:
        score += 1.5
    if online_score_req.first_name and online_score_req.last_name:
        score += 0.5
    return score


def get_interests(store, cid):
    interests = ["cars", "pets", "travel", "hi-tech", "sport", "music", "books", "tv", "cinema", "geek", "otus"]
    return random.sample(interests, 2)
