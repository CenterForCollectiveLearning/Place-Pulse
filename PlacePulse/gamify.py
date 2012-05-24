from db import Database

class Gamification(object):
    GamifySettings = {
        "VoteUnlockPoints": {
            # Map number of votes to study ID results to unlock
            5: '4fad3e2c1fdcef82b8003ec6',
            25: '4fad3e2c1fdcef82b8003ec5'
        }
    }
    @classmethod
    def unlockNew(cls,userObj):
        studiesUnlocked = []
        for numVotesToUnlock,unlockableStudy in cls.GamifySettings['VoteUnlockPoints'].iteritems():
            if unlockableStudy not in userObj.get('unlocked_studies',[]) and userObj.get('num_votes',0) >= numVotesToUnlock:
                studiesUnlocked.append(unlockableStudy)
        return studiesUnlocked
    @classmethod
    def nextToUnlock(cls,userObj):
        voteUnlockPoints = cls.GamifySettings['VoteUnlockPoints'].items()
        nextUnlockableStudy = None
        for unlockableStudy in voteUnlockPoints:
            # Skip over studies already unlocked
            if unlockableStudy[1] in userObj.get('unlocked_studies',[]): continue
            if nextUnlockableStudy:
                if userObj.get('num_votes',0) < unlockableStudy[0]:
                    nextUnlockableStudy = min(nextUnlockableStudy,unlockableStudy,key=lambda x:x[0])
            else:
                # Set nextUnlockableStudy to the study we see that hasn't yet been unlocked
                nextUnlockableStudy = unlockableStudy
        return nextUnlockableStudy
    @classmethod
    def getUnlockStatus(cls,userObj):
        # userObj may not exist for new or uncookied users
        if userObj is None: userObj = dict()
        nextStudy = cls.nextToUnlock(userObj)
        return {
            "nextStudy": {
                "studyID": nextStudy[1],
                "votesToUnlock": nextStudy[0],
                "studyQuestion": Database.getStudyQuestion(nextStudy[1])
            },
            "numVotes": userObj.get('num_votes',0),
            "lastUnlockedAt": userObj.get('last_unlocked_at',0)
        }