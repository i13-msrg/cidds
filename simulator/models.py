from django.contrib.auth.models import User
from django.db import models
from safedelete.models import SafeDeleteModel
import uuid
import os

def get_image_path(instance, filename):
    return os.path.join('simulationresults', str(instance.id), filename)

class SimulationResults(SafeDeleteModel):
    # unique id for each simulation
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # reference text for the simulation
    reference =  models.TextField(blank=True,
                                  help_text= "A short description of the simulation" )

    tangle = models.TextField(blank=True,
                                  help_text= "The tangle result from the simulation" )
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)

    user = models.ForeignKey(
        User,
        null=True,
        editable=False,
        on_delete=models.PROTECT,
        verbose_name="Created by user",
        help_text="User who created the simulation"
    )

