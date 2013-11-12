"""
Constants file
"""

DEBUG = True

HISCORE_URL = "http://grymark.us.to/hiscore"

FPS = 60
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500

# Game
GAME_WINDOW_X0 = WINDOW_WIDTH/4
GAME_WINDOW_Y0 = 0
GAME_WINDOW_WIDTH = 3*WINDOW_WIDTH/4
GAME_WINDOW_HEIGHT = WINDOW_HEIGHT
GAME_MODE = {'SINGLE_ADVENTURE':0, 'MULTI_COOP':1, 'MULTI_CLASSIC':2, 'MULTI_BALL':3}
STATE = {'PAUSED':0, 'IN_PROGRESS':1, 'NEW_LIFE':2, 'LEVEL_END':3, 'GAME_END':4, 'GAME_OVER':5, 'SCORE_COUNTING':6, 'SCORE_END':7}
SCREEN = {'GAMEBOARD':0, 'STATEBOARD':1}
DEFAULT_TIME = 60

# Player
PLAYER_COLOR = [
	(255,255,0),
	(0,255,255),
	(255,0,255),
	(0,255,0)
]
NB_LIVES = {'INIT':3, 'MAX':5}
SCORE_BONUS_MIN = 1
SCORE_CHAIN_BONUS = [0,0,1,3,3,5,7,10,15,15,20,20,20,50]
BONUS_TYPE = {'PERFECT':0, 'TIME':1}
BONUS_INDEX = {'LBL':0, 'VALUE':1}
BONUS = [
	['PERFECT BONUS', 50],
	['TIME BONUS', 'value']
]

# Ball
BALL_COLOR = (178,34,34)
BALL_CURVING_COLOR = (255,102,0)
BALL_RADIUS = 8
BALL_SPEED_MIN = 1
BALL_SPEED_MAX = 6 															# 6 easy, 8 medium, 10 hard
BALL_FACTOR = 0.4
BALL_CURVE_FACTOR = 0.2
DIRECTION = {'X':{'LEFT':-1, 'RIGHT':1}, 'Y':{'UP':-1, 'DOWN':1}}

# Paddle
PADDLE_COLOR = (0,0,255)
PADDLE_WIDTH = {'INIT':70, 'MIN':30, 'MAX':140}
PADDLE_HEIGHT = 10
PADDLE_H_SPEED = {'INIT':4, 'MIN':2, 'MAX':8}
PADDLE_V_SPEED = {'INIT':3, 'MIN':2, 'MAX':4}								# Should be below BALL_SPEED_MAX to avoid collision problems
PADDLE_FACTOR = 1.1
PADDLE_GRAVITY = 1.0
PAD_GROWTH = 14.0
PAD_BOOST = {'INIT':10.0, 'MIN':5.0, 'MAX':20.0} 							# Number of seconds in boost
PAD_BOOST_GAIN = 2.0 														# Boost seconds gained per rest second
PAD_BOOST_FRACTION = 1.0/3.0												# Fraction of boost max necessary to start boosting
H_BOOST_COST = 20.0 														# Horizontal boost costs H_BOOST_COST times more
H_BOOST_FACTOR = 1.0														# Speed multiplied by 1 + H_BOOST_FACTOR during boosts
BOOST_COLOR = {'DEFAULT':(255,0,0), 'RELOAD':(0,150,0), 'OUTOF':(0,0,0)}
PADDLE_TRAIL_LEN = 5 														# Number of pads printed when boost
PAD_BOOST_TXT_SZ = 10 														# Size of boost value
PAD_BOTTOM_LIMIT = GAME_WINDOW_HEIGHT-PADDLE_HEIGHT							# Pad cannot go under

# Brick
BRICK_WIDTH = 50
BRICK_HEIGHT = 10
NB_BRICK_BY_ROW_MAX = GAME_WINDOW_WIDTH/BRICK_WIDTH
NB_ROW_MAX = 40
BRICK_TYPE = {'NORMAL':1, 'HARD':2, 'VHARD':3, 'STEEL':4, 'DEVIL':5, 'SATAN':6, 'NITRO':7, 'MASSIVE':8} # 9 black(made destructible by key)
BRICK_CHAR_INDEX = {'RES':0, 'COLOR':1, 'BONUS':2}
BRICK_CHAR = [
	None,
	[1,(255,255,0),1],
	[2,(0,112,224),3],
	[3,(0,0,224),5],
	[-1,(105,105,105),0],
	[1,(204,0,0),-10],
	[1,(102,0,0),-20],
	[1,(99,255,20),0],
	[1,(255,0,179),0]
]
BRICK_DESC = [
	"No brick.",
	"Normal brick (1 hit).",
	"Hard brick (2 hits).",
	"Very hard brick (3 hits).",
	"Indestructible brick.",
	"Devil brick.",
	"Satan brick.",
	"Nitro brick.",
	"Massive brick."
]
NEG_BRICK_POS_SCORE = 2 # Score obtained when brick 5 or 6 hit AFTER all other bricks

# Usable
USABLE_DIM = 15
USABLE_TYPE = {'PAD_SPEEDUP':1, 'PAD_GROW':2, 'PAD_SHRINK':3, 'PAD_BOOST':4, 'PLA_LIFEUP':5}
USABLE_CHAR_INDEX = {'COLOR':0, 'SPEED':1, 'TO':2}
USABLE_CHAR = [
	None,
	[(148,0,211), 4, 'PADDLE'],
	[(0,0,255), 4, 'PADDLE'],
	[(255,0,0), 4, 'PADDLE'],
	[(255,105,180), 4, 'PADDLE'],
	[(255,255,255), 4, 'PLAYER']
]
USABLE_DESC = [
	"No effect.",
	"Paddle speed ++",
	"Paddle size ++",
	"Paddle size --",
	"Paddle boost ++"
]

# Visual effect
VEF_TXT_COLOR = (255,255,0)			# Score notification default color
VEF_NEG_TXT_COLOR = (255,0,0)		# Score notification color for negative value 
VEF_TXT_SZ = 20 					# Score notification size
VEF_SCORE_TIMER = 700				# Score notification timer
VEF_PAD_GROW_COLOR = (0,0,255)		# Pad growing arrows color
VEF_PAD_SHRINK_COLOR = (255,0,0)	# Pad shrinking arrows color
VEF_PAD_GROW_TIMER = 500			# Pad growing arrows timer
VEF_PAD_BOOST_LBL = '+BOOST+'		# Pad boost up vef label
VEF_PAD_SPDUP_LBL = 'SPEED UP'		# Pad speed up vef label
VEF_PAD_LIFEUP_LBL = 'LIFE +1'		# Player life up vef label
VEF_PAD_LBL_COLOR = (0,0,255)		# Pad vef notifications color


# Global
DEFAULT_COLOR = (0,0,0)
DEF_ALPHA_COLOR = (181,230,29)
SHAPE = {'CIRCLE':0, 'RECT':1}
DEFAULT_BORDER_WIDTH = 1
TEXT_ALIGN = {'H':{'LEFT':0, 'CENTER':1, 'RIGHT':2}, 'V':{'TOP':0, 'MIDDLE':1, 'BOTTOM':2}}
LVL_DIR = './lvl/'
LVL_FORMAT = '.txt'
SOUND_DIR = 'data/sounds/'
IMAGE_DIR = 'data/images/'
PLAYERS_DIR = 'data/players/'

# Font style
GLOBAL_FONT = 'Verdana'

# Font color
GLOBAL_LABEL_COLOR = (165,42,42)
GLOBAL_MENU_COLOR = (255,255,255)
BG_COLOR = (70,130,180)
MENU_BG_COLOR = (0,0,0)
SCORE_BG_COLOR = (0,0,0)
SCORE_LBL_COLOR = (255,255,255)
TROPHY_PLAYER_COLOR = (165,42,42)

# Font size
GO_LBL_SZ = 40
MENU_LBL_SZ_S = 15
MENU_LBL_SZ_XS = 12
RESUME_LBL_SZ = 25
GO_RESTART_LBL_SZ = 15
BONUS_SZ = 15
TIME_SZ = 20
SCORE_SZ = 20
TROPHY_REF_SZ = 12
NEW_RECORD_SZ = 30

# Menu interspace
MENU_SPACE_S = 5
MENU_SPACE_M = 10

# Labels
WINDOW_TITLE = "Grymark"
GO_LBL = 'GAME OVER'
MENU_LEVEL_LBL = 'LEVEL'
MENU_AUTHOR_LBL = 'AUTHOR'
MENU_LIVES_LBL = 'LIVES'
MENU_SCORE_LBL = 'SCORE'
SCORE_LVL_LBL = 'LEVEL SCORE'
SCORE_TOTAL_LBL = 'TOTAL SCORE'
NEW_RECORD_LBL = 'NEW RECORD!'
WORLD_RECORD_LBL = 'WORLD RECORD!'

MENU_TIME_LBL = 'TIME'
MENU_LOCAL_TIME_LBL = 'PR'
MENU_WORLD_TIME_LBL = 'WR'
RESUME_LBL = 'Press SPACE to resume game'
GO_RESTART_LBL = 'Press Y to continue, N to ragequit'
NO_TROPHY_LBL = 'No trophy, you suck!'

# Score board
SB_X0 = GAME_WINDOW_WIDTH/4+50
SB_Y0 = 50
SB_WIDTH = GAME_WINDOW_WIDTH*3/4-100
SB_HEIGHT = GAME_WINDOW_HEIGHT-100
SB_CONTENT_X0 = MENU_SPACE_M*3
SB_NEWREC_Y0 = MENU_SPACE_M
SB_SCORE_Y0 = MENU_SPACE_M*6
SB_TROPHY_Y0 = GAME_WINDOW_WIDTH/2+MENU_SPACE_M*5
# Game over board
GOB_X0 = GAME_WINDOW_WIDTH/4+50
GOB_Y0 = SB_TROPHY_Y0
GOB_WIDTH = GAME_WINDOW_WIDTH*3/4-100
GOB_HEIGHT = GAME_WINDOW_HEIGHT/5