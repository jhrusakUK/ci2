from django.db import models

class SmilesQuery(models.Model):
    smiles = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.smiles} ({self.created_at})"
