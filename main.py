import pygame
import sys
import os
import time

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Alarms")
WIDTH, HEIGHT = screen.get_size()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

ALARM_DELAY_SECONDS = 5

sound_dir = os.path.join(os.path.dirname(__file__), 'sounds')
os.makedirs(sound_dir, exist_ok=True)
names = []

if not os.path.exists(os.path.join(os.path.dirname(__file__), '.habitimer')):
    os.makedirs(os.path.join(os.path.dirname(__file__), '.habitimer'), exist_ok=True)
if not os.path.exists(os.path.join(os.path.dirname(__file__), '.habitimer/names.txt')):
    with open(os.path.join(os.path.dirname(__file__), '.habitimer/names.txt'), "w") as f:
        f.write("")

with open(os.path.join(os.path.dirname(__file__), '.habitimer/names.txt')) as f: 
    for name in f.readlines():
        names.append(name[:-1])

if len(names) < 6:
    num_missing = 6 - len(names)
    for i in range(num_missing):
        new_name = input(f"Enter name {len(names) + 1}: ").strip()
        names.append(new_name)
    with open(os.path.join(os.path.dirname(__file__), '.habitimer/names.txt'), "w") as f:
        for name in names:
            f.write(name + "\n")
ALARM_DELAY_SECONDS = 7200

sound_dir = os.path.join(os.path.dirname(__file__), 'sounds')
os.makedirs(sound_dir, exist_ok=True)
names = ["Kapi", "Gabi", "Olek", "Dobi", "Natalka", "Eleonora"]

alarm_sound_path = os.path.join(sound_dir, 'alarm.mp3')

try:
    alarm_sound = pygame.mixer.Sound(alarm_sound_path)
    alarm_sound.play(-1)  # -1 means loop indefinitely
except pygame.error:
    alarm_sound = None
    print(f"Error loading sound. Please ensure '{alarm_sound_path}' is a valid sound file.")

class Checkbox:
    def __init__(self, x, y, size=50, name=""):
        self.rect = pygame.Rect(x, y, size, size)
        self.checked = False
        self.size = size
        self.check_time = None
        self.name = name
    
    def draw(self, surface):
        if self.name:
            name_font = pygame.font.SysFont(None, 36)
            name_text = name_font.render(self.name, True, WHITE)
            name_rect = name_text.get_rect(centerx=self.rect.centerx, bottom=self.rect.top - 5)
            surface.blit(name_text, name_rect)
            
        pygame.draw.rect(surface, WHITE, self.rect, 3)
        
        if self.checked:
            inner_rect = pygame.Rect(
                self.rect.x + 5, 
                self.rect.y + 5, 
                self.rect.width - 10, 
                self.rect.height - 10
            )
            pygame.draw.rect(surface, GREEN, inner_rect)
            
            if self.check_time is not None:
                elapsed = time.time() - self.check_time
                remaining = max(0, ALARM_DELAY_SECONDS - elapsed) 
                hours = int(remaining // 3600)
                minutes = int((remaining % 3600) // 60)
                seconds = int(remaining % 60)
                
                small_font = pygame.font.SysFont(None, 24)
                time_text = small_font.render(f"{hours:02d}:{minutes:02d}:{seconds:02d}", True, WHITE)
                time_rect = time_text.get_rect(center=(self.rect.centerx, self.rect.centery))
                surface.blit(time_text, time_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.checked:
                    self.check_time = time.time()
                else:
                    self.check_time = None
                return True
        return False
    
    def update(self):
        if self.checked and self.check_time is not None:
            elapsed = time.time() - self.check_time
            if elapsed >= ALARM_DELAY_SECONDS:
                self.checked = False
                self.check_time = None
                return True
        return False

checkboxes = []
checkbox_size = 80

positions = [
    (WIDTH // 4, HEIGHT // 3),
    (WIDTH // 2, HEIGHT // 3),
    (WIDTH * 3 // 4, HEIGHT // 3),
    (WIDTH // 4, HEIGHT * 2 // 3),
    (WIDTH // 2, HEIGHT * 2 // 3),
    (WIDTH * 3 // 4, HEIGHT * 2 // 3)
]


for i, pos in enumerate(positions):
    name = names[i] if i < len(names) else f"Check {i+1}"
    checkboxes.append(Checkbox(
        pos[0] - checkbox_size // 2, 
        pos[1] - checkbox_size // 2, 
        checkbox_size,
        name
    ))

font = pygame.font.SysFont(None, 48)

running = True
completed = False
clock = pygame.time.Clock()
any_checkbox_was_checked = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        
        for checkbox in checkboxes:
            if checkbox.handle_event(event):
                if checkbox.checked:
                    any_checkbox_was_checked = True
    
    screen.fill(BLACK)
    
    for checkbox in checkboxes:
        checkbox.draw(screen)
    
    any_unchecked = any(not checkbox.checked for checkbox in checkboxes)
    
    if any_unchecked:
        if alarm_sound and not pygame.mixer.get_busy():
            alarm_sound.play(-1)
    else:
        if alarm_sound:
            alarm_sound.stop()
    
    all_checked = all(checkbox.checked for checkbox in checkboxes)
    
    if all_checked and not completed:
        completed = True
        
    if all_checked:
        text = font.render("Good job crew! See you soon", True, GREEN)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
    elif not os.path.exists(alarm_sound_path):
        text = font.render("Please add an alarm sound file at: " + alarm_sound_path, True, RED)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
    
    pygame.display.flip()
    
    clock.tick(30)

if alarm_sound:
    alarm_sound.stop()
pygame.quit()
sys.exit()
