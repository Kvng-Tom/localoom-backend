from django.db import migrations, models
from django.db.utils import ProgrammingError

def add_slug_column(apps, schema_editor):
    try:
        schema_editor.execute("ALTER TABLE store_product ADD COLUMN slug VARCHAR(255);")
    except ProgrammingError:
        # Skip adding the column if it already exists
        pass

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_product_sku_review'),
    ]

    operations = [
        migrations.RunPython(add_slug_column),
    ]