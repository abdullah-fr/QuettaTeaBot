"""
Expandable question banks with tracking to avoid repetition
Questions are randomly selected and tracked to prevent repeats
"""

# ==================== QOTD QUESTIONS (Expandable) ====================
QOTD_QUESTIONS = [
    "What's your favorite childhood memory?",
    "If you could have dinner with anyone, dead or alive, who would it be?",
    "What's the best advice you've ever received?",
    "If you could live anywhere in the world, where would it be?",
    "What's your hidden talent?",
    "What's something you're really proud of?",
    "If you could master any skill instantly, what would it be?",
    "What's your favorite way to spend a weekend?",
    "What's the most interesting place you've ever visited?",
    "If you could time travel, would you go to the past or future?",
    "What's your comfort food?",
    "What's a book/movie that changed your perspective?",
    "What's your biggest fear and why?",
    "If you won the lottery, what's the first thing you'd do?",
    "What's your favorite season and why?",
    "What's something you wish you knew more about?",
    "What's your dream job?",
    "What's the best gift you've ever received?",
    "If you could have any superpower, what would it be?",
    "What's your favorite memory from this year?",
    "What's something that always makes you smile?",
    "What's your biggest accomplishment?",
    "If you could learn any language, which one?",
    "What's your favorite hobby?",
    "What's the most adventurous thing you've done?",
    "What's your go-to karaoke song?",
    "What's something you're currently learning?",
    "What's your favorite quote?",
    "If you could meet your younger self, what would you say?",
    "What's your favorite thing about yourself?",
]

# ==================== WOULD YOU RATHER ====================
WYR_QUESTIONS = [
    "Would you rather have the ability to fly or be invisible?",
    "Would you rather live in the past or the future?",
    "Would you rather have unlimited money or unlimited time?",
    "Would you rather never use social media again or never watch another movie?",
    "Would you rather be able to talk to animals or speak all languages?",
    "Would you rather live without music or without movies?",
    "Would you rather be famous or be the best friend of someone famous?",
    "Would you rather explore space or the deep ocean?",
    "Would you rather always be 10 minutes late or 20 minutes early?",
    "Would you rather have a rewind button or a pause button for your life?",
    "Would you rather be able to read minds or see the future?",
    "Would you rather live in a world without problems or a world without challenges?",
    "Would you rather have free Wi-Fi wherever you go or free coffee?",
    "Would you rather be the funniest person or the smartest person?",
    "Would you rather never have to sleep or never have to eat?",
    "Would you rather live in a big city or a small town?",
    "Would you rather be a master chef or a master musician?",
    "Would you rather have a photographic memory or be able to forget anything?",
    "Would you rather always say what you think or never speak again?",
    "Would you rather be able to control fire or water?",
]

# ==================== CONVERSATION STARTERS ====================
CONVERSATION_STARTERS = [
    "What's the most interesting thing that happened to you this week?",
    "If you could learn any skill instantly, what would it be?",
    "What's your go-to comfort food?",
    "Share a fun fact about yourself!",
    "What's the last thing that made you laugh?",
    "What's your favorite way to relax?",
    "If you could visit any country, where would you go?",
    "What's your favorite childhood game?",
    "What's something you're looking forward to?",
    "What's the best concert or show you've been to?",
    "What's your favorite type of music?",
    "If you could have any pet, what would it be?",
    "What's your favorite holiday and why?",
    "What's something you've always wanted to try?",
    "What's your favorite thing to do on a rainy day?",
    "What's the best meal you've ever had?",
    "If you could switch lives with anyone for a day, who would it be?",
    "What's your favorite app on your phone?",
    "What's something that made you smile today?",
    "What's your dream vacation destination?",
]

# ==================== COMPLIMENTS ====================
COMPLIMENTS = [
    "You're an awesome friend!",
    "You light up the room!",
    "You're more helpful than you realize!",
    "You have a great sense of humor!",
    "You're a great listener!",
    "You're incredibly talented!",
    "You make a positive difference!",
    "You're one of a kind!",
    "You're a joy to be around!",
    "You're stronger than you think!",
    "You have impeccable manners!",
    "You're a great example to others!",
    "You're always learning and growing!",
    "You have a great taste!",
    "You're really courageous!",
]

# ==================== ROASTS (Friendly & SFW) ====================
ROASTS = [
    "You're like a software update. Whenever I see you, I think 'Not now.'",
    "I'd agree with you, but then we'd both be wrong.",
    "You bring everyone so much joy... when you leave the room.",
    "You're like a cloud. When you disappear, it's a beautiful day.",
    "I'd explain it to you, but I left my crayons at home.",
    "You're not stupid; you just have bad luck when thinking.",
    "I'm jealous of people who don't know you.",
    "You're the reason the gene pool needs a lifeguard.",
    "If laughter is the best medicine, your face must be curing the world.",
    "You're like Monday mornings - nobody likes you.",
    "I'd call you a tool, but that would imply you're useful.",
    "You're proof that even trash can be recycled.",
    "You have the perfect face for radio.",
    "You're like a participation trophy - everyone gets one, but nobody wants it.",
    "If I had a dollar for every smart thing you say, I'd be broke.",
]

# ==================== SONGS FOR GUESSING ====================
SONGS = [
    # Pakistani Classics
    {"lyrics": "Dil dil Pakistan, jaan jaan Pakistan", "answer": "Dil Dil Pakistan"},
    {"lyrics": "Aye watan pyare watan pak watan", "answer": "Aye Watan Pyare Watan"},
    {"lyrics": "Mera bichra yaar mujhe aaj mil gaya", "answer": "Mera Bichra Yaar"},
    {"lyrics": "Dil ki lagi na mano", "answer": "Dil Ki Lagi"},
    {"lyrics": "Tera woh pyar yaad hai mujhe", "answer": "Tera Woh Pyar"},

    # Pakistani Modern
    {"lyrics": "Aadat si hai mujhko aise jeene mein", "answer": "Aadat"},
    {"lyrics": "Tera mera rishta purana", "answer": "Tera Mera Rishta"},
    {"lyrics": "Sayonee mere dil ki", "answer": "Sayonee"},
    {"lyrics": "Duur na jaana", "answer": "Duur"},
    {"lyrics": "Khudi ko kar buland itna", "answer": "Khudi"},

    # Indian Classics
    {"lyrics": "Mere sapno ki rani kab aayegi tu", "answer": "Mere Sapno Ki Rani"},
    {"lyrics": "Yeh dosti hum nahi todenge", "answer": "Yeh Dosti"},
    {"lyrics": "Kabhi kabhi mere dil mein khayal aata hai", "answer": "Kabhi Kabhi"},
    {"lyrics": "Tum hi ho bandhu sakha tumhi", "answer": "Tum Hi Ho"},
    {"lyrics": "Lag ja gale ke phir ye haseen raat ho na ho", "answer": "Lag Ja Gale"},

    # Indian Modern/Bollywood
    {"lyrics": "Tum hi ho tum hi ho zindagi ab tum hi ho", "answer": "Tum Hi Ho"},
    {"lyrics": "Tujhe dekha to ye jaana sanam", "answer": "Tujhe Dekha To"},
    {"lyrics": "Chaiyya chaiyya chaiyya chaiyya", "answer": "Chaiyya Chaiyya"},
    {"lyrics": "Kal ho naa ho kal ho naa ho", "answer": "Kal Ho Naa Ho"},
    {"lyrics": "Kuch kuch hota hai tum nahi samjhoge", "answer": "Kuch Kuch Hota Hai"},

    # Famous English Songs
    {"lyrics": "I'm walking on sunshine, whoa oh", "answer": "Walking on Sunshine"},
    {"lyrics": "Is this the real life? Is this just fantasy?", "answer": "Bohemian Rhapsody"},
    {"lyrics": "Just a small town girl, living in a lonely world", "answer": "Don't Stop Believin'"},
    {"lyrics": "I got the eye of the tiger, a fighter", "answer": "Eye of the Tiger"},
    {"lyrics": "We will, we will rock you", "answer": "We Will Rock You"},
    {"lyrics": "Hello from the other side", "answer": "Hello"},
    {"lyrics": "Cause baby you're a firework", "answer": "Firework"},
    {"lyrics": "I'm gonna swing from the chandelier", "answer": "Chandelier"},
    {"lyrics": "Shake it off, shake it off", "answer": "Shake It Off"},
    {"lyrics": "We found love in a hopeless place", "answer": "We Found Love"},
    {"lyrics": "I will always love you", "answer": "I Will Always Love You"},
    {"lyrics": "Sweet dreams are made of this", "answer": "Sweet Dreams"},
    {"lyrics": "Don't stop me now, I'm having such a good time", "answer": "Don't Stop Me Now"},
    {"lyrics": "Imagine all the people living life in peace", "answer": "Imagine"},
    {"lyrics": "Hey Jude, don't make it bad", "answer": "Hey Jude"},
]

# ==================== URDU POETRY ====================
URDU_POETRY = [
    "دل کی ویرانی کا کیا مذکور ہے\nیہ نگر سو مرتبہ لوٹا گیا",
    "محبت کرنے والے کم نہ ہوں گے\nتری محفل میں لیکن ہم نہ ہوں گے",
    "ہزاروں خواہشیں ایسی کہ ہر خواہش پہ دم نکلے\nبہت نکلے مرے ارمان لیکن پھر بھی کم نکلے",
    "کبھی ہم خوب تھے، کبھی ہم خوب تھے\nکبھی ہم خوب تھے، کبھی ہم خوب تھے",
    "یہ دنیا اگر مل بھی جائے تو کیا ہے\nیہ دنیا اگر مل بھی جائے تو کیا ہے",
]

# ==================== PICTIONARY WORDS ====================
PICTIONARY_WORDS = [
    "cat", "dog", "house", "tree", "car", "sun", "moon", "star",
    "flower", "book", "phone", "computer", "pizza", "burger", "cake",
    "guitar", "piano", "drum", "rainbow", "cloud", "mountain", "beach",
    "bicycle", "airplane", "boat", "train", "elephant", "lion", "bird",
    "fish", "butterfly", "spider", "snake", "turtle", "rocket", "castle"
]

# ==================== PETS ====================
PETS = ["🐶 Dog", "🐱 Cat", "🐰 Rabbit", "🐹 Hamster", "🐦 Bird",
        "🐠 Fish", "🐢 Turtle", "🦎 Lizard", "🐷 Pig", "🐸 Frog"]

# ==================== COLLECTIBLE ITEMS ====================
ITEMS = ["🍎 Apple", "🍕 Pizza", "💎 Diamond", "🎁 Gift Box", "⚔️ Sword",
         "🛡️ Shield", "🏹 Bow", "🔮 Crystal Ball", "📿 Amulet", "👑 Crown",
         "🎨 Paint Brush", "📚 Ancient Book", "🗝️ Golden Key", "💰 Treasure Chest"]

def get_random_question(question_list, asked_list, max_history=50):
    """
    Get a random question that hasn't been asked recently
    Resets history if all questions have been used
    """
    available = [q for q in question_list if q not in asked_list]

    if not available:
        # All questions used, reset history
        asked_list.clear()
        available = question_list

    question = random.choice(available)
    asked_list.append(question)

    # Keep only last N questions in history
    if len(asked_list) > max_history:
        asked_list.pop(0)

    return question
