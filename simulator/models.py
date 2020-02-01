from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model
from django.utils import timezone
from safedelete.models import SafeDeleteModel
import uuid
import os

def get_image_path(instance, filename):
    return os.path.join('simulation_results', str(instance.id), filename)

class SimulationResults(Model):

    # User who initiated the error
    user = models.ForeignKey(
        User,
        null=True,
        editable=False,
        on_delete=models.PROTECT,
        verbose_name="Created by user",
        help_text="User who created the simulation"
    )
    # Number of processes
    num_process = models.IntegerField(blank=True, null=True, default= 1)

    # Number of transactions
    transactions = models.IntegerField(blank=True, null=True, default = 10)

    alpha = models.FloatField(blank=True, null=True, default=1)

    numTotalUser = models.IntegerField(blank=True, null=True, default = 3)
    numMalUser = models.IntegerField(blank=True, null=True, default = 0)
    traUser = models.IntegerField(blank=True, null=True, default = 5)
    nodeReattachment = models.BooleanField(blank=True, null=True, default = True)

    # Degree of randomness
    randomness = models.FloatField(blank=True, null=True, default=1)

    # Tip selection algorithm
    algorithm = models.CharField(blank=True, max_length=10,
                                help_text="A short description of the simulation")

    # reference text for the simulation
    reference =  models.TextField(blank=True,
                                  help_text= "A short description of the simulation" )

    # Picked version of the entire tangle
    dag = models.TextField(blank=True,
                           help_text= "The tangle result from the simulation")

    # Current status of the simulation - Can be running or done
    status = models.CharField(blank=True, max_length=20,
                                help_text="Status of the simulation")


    # resultant plotted image
    image = models.ImageField(upload_to='result_images', blank=True, null=True)

    # Created time
    created = models.DateTimeField(editable=False, default=timezone.now)

    # modified time
    modified = models.DateTimeField(null=True)

    # Time units
    time_units = models.FloatField(blank=True, null=True, default=0)

    # unapproved tips
    unapproved_tips = models.IntegerField(blank=True, null=True, default = 0)


    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(SimulationResults, self).save(*args, **kwargs)






