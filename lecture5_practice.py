import pandas as pd
from psychopy.gui import DlgFromDict
from psychopy.visual import Window, TextStim, ImageStim, Slider
from psychopy.core import Clock, quit, wait
from psychopy.event import Mouse
from psychopy.hardware.keyboard import Keyboard

### DIALOG BOX ROUTINE ###
exp_info = {'participant_nr': '', 'age': ''}
dlg = DlgFromDict(exp_info)

# If pressed Cancel, abort!
if not dlg.OK:
    quit()
else:
    # Quit when either the participant nr or age is not filled in
    if not exp_info['participant_nr'] or not exp_info['age']:
        quit()
        
    # Also quit in case of invalid participant nr or age
    if int(exp_info['participant_nr']) > 99 or int(exp_info['age']) < 18:
        quit()
    else:  # let's star the experiment!
        print(f"Started experiment for participant {exp_info['participant_nr']} "
                 f"with age {exp_info['age']}.")

# Initialize a fullscreen window with my monitor (HD format) size
# and my monitor specification called "samsung" from the monitor center
win = Window(size=(800, 400), fullscr=False, monitor='samsung')

# Also initialize a mouse, although we're not going to use it
mouse = Mouse(visible=True)

# Initialize a (global) clock
clock = Clock()

# Initialize Keyboard
kb = Keyboard()
kb.clearEvents()

### START BODY OF EXPERIMENT ###


### WELCOME ROUTINE ###
# Create a welcome screen and show for 2 seconds
welcome_txt_stim = TextStim(win, text="Welcome to this experiment!", color=(1, 0, -1), font='Calibri')
welcome_txt_stim.draw()
win.flip()
wait(2)

### INSTRUCTION ROUTINE ###
instruct_txt = """ 

In this task, you will see a series of letter strings.
Your job is to decide whether each string is a real English word or a nonsense (fake) word.

    If the word is REAL, press the LEFT arrow key.
    If the word is NOT REAL (a fake word), press the RIGHT arrow key.

Please respond as quickly and accurately as possible.

Press ‘enter’ to start the experiment!
"""

# Show instructions and wait until response (return)
instruct_txt = TextStim(win, instruct_txt, alignText='left', height=0.085)
instruct_txt.draw()
win.flip()

# Initialize keyboard and wait for response
kb = Keyboard()
while True:
    keys = kb.getKeys()
    if any(key.name == 'return' for key in keys):
        # The for loop was optional
        for key in keys:
            print(f"The {key.name} key was pressed within {key.rt:.3f} seconds for a total of {key.duration:.3f} seconds.")
        break  # break out of the loop!



### TRIAL LOOP ROUTINE ###
# Read in conditions file
cond_df = pd.read_excel('word_conditions.xlsx')
cond_df = cond_df.sample(frac=1)#take 100% rows in the file for random selection

# Create fixation target (a plus sign)
fix_target = TextStim(win, '+')
trial_clock = Clock()

# START exp clock
clock.reset()

# Show initial fixation
fix_target.draw()
win.flip()
wait(1)

for idx, row in cond_df.iterrows():
    # Extract current word and whether it is a word
    curr_stim = row['stim']
    curr_word = row['word']

    # Create and draw text/img
    stim_txt = TextStim(win, curr_stim)

    # Initially, onset is undefined
    cond_df.loc[idx, 'onset'] = -1

    trial_clock.reset()
    kb.clock.reset()
    cond_df.loc[idx, 'correct'] = -1
    while trial_clock.getTime() < 2:
        # Draw stuff
        
        if trial_clock.getTime() < 0.5:
            fix_target.draw()
        else:
            stim_txt.draw()
            
        win.flip()
        if cond_df.loc[idx, 'onset'] == -1:
            cond_df.loc[idx, 'onset'] = clock.getTime()#record the onset time of each trial
        
        # Get responses
        resp = kb.getKeys()
        if resp:
            # Stop the experiment when 'q' is pressed
            if 'q' in resp:
                quit()

            # Log reaction time and response
            cond_df.loc[idx, 'rt'] = resp[-1].rt
            cond_df.loc[idx, 'resp'] = resp[-1].name

            # Log correct/incorrect
            if resp[-1].name == 'left' and curr_word == 'yes':
               cond_df.loc[idx, 'correct'] = 1
            elif resp[-1].name ==  'right' and curr_word == 'no':
                cond_df.loc[idx, 'correct'] = 1
            elif resp[-1].name ==  'left' and curr_word == 'no':
                cond_df.loc[idx, 'correct'] = 0
            elif resp[-1].name ==  'right' and curr_word == 'yes':
                cond_df.loc[idx, 'correct'] = 0



effect = cond_df.groupby('word').mean(numeric_only=True)
rt_yes = effect.loc['yes', 'rt']
rt_no = effect.loc['no', 'rt']
acc = cond_df['correct'].mean()

txt = f"""
Your reaction times are as follows:

   Word:{rt_yes:.3f}
   Non-Word:{rt_no:.3f}

Overall accuracy: {acc:.3f}
"""
result = TextStim(win, txt)
result.draw()
win.flip()
wait(5)


cond_df.to_csv(f"sub-{exp_info['participant_nr']}_results.csv")


#add a mouse action
feedback_stim = TextStim(win, text="Please rate your feelings now", pos=(0,0.4))
feedback_stim.draw()

# Create a Slider
slider = Slider(win, ticks=[1, 2, 3, 4, 5],
                labels=['Very Bad', '', 'Neutral', '', 'Very Good'],
                granularity=1, style='rating', pos=(0, 0), size=(1.2, 0.1))

slider.draw()
win.flip()


mouse = Mouse(win=win)
rating_made = False

while not rating_made:
    if slider.getRating() is not None and mouse.getPressed()[0]: 
        rating_made = True
    slider.draw()
    feedback_stim.draw()
    win.flip()


final_rating = slider.getRating()
print(f"Participant's rating: {final_rating}")


# Finish experiment by closing window and quitting
win.close()
quit()  