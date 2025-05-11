from PIL import Image, ImageDraw, ImageFont
import os

# Créer un dossier pour le logo si nécessaire
os.makedirs('static/img', exist_ok=True)

# Créer une image avec un fond blanc
width, height = 300, 150
image = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(image)

# Dessiner un rectangle bleu comme fond du logo
draw.rectangle([(0, 0), (width, height)], fill='#2c3e50')

# Ajouter le texte "MAMO" en blanc
try:
    # Essayer de charger une police
    font = ImageFont.truetype("arial.ttf", 60)
except IOError:
    # Si la police n'est pas disponible, utiliser la police par défaut
    font = ImageFont.load_default()

# Dessiner le texte "MAMO" centré
text = "MAMO"
text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (150, 60)
position = ((width - text_width) // 2, (height - text_height) // 2)
draw.text(position, text, fill='white', font=font)

# Sauvegarder l'image
logo_path = 'static/img/logo_mamo.png'
image.save(logo_path)

print(f"Logo créé avec succès: {logo_path}")
