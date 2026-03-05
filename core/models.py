from django.db import models
from django.contrib.auth.models import User
from datetime import date

# ---------------------
# RESIDENT
# ---------------------
class Resident(models.Model):

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)

    birthday = models.DateField(null=True, blank=True)

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )

    civil_status = models.CharField(max_length=20, blank=True)
    purok = models.CharField(max_length=50, blank=True)
    zone = models.CharField(max_length=50, blank=True)

    contact_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def full_name(self):
        return f"{self.firstname} {self.lastname}"

    @property
    def age(self):
        if self.birthday:
            today = date.today()
            return today.year - self.birthday.year - (
                (today.month, today.day) <
                (self.birthday.month, self.birthday.day)
            )
        return None

    def __str__(self):
        return self.full_name


# ---------------------
# PROJECT
# ---------------------
class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_started = models.DateField(null=True, blank=True)

    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned'
    )

    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ ADD THESE PROPERTIES
    @property
    def like_count(self):
        return self.reactions.filter(reaction='like').count()

    @property
    def dislike_count(self):
        return self.reactions.filter(reaction='dislike').count()

    def __str__(self):
        return self.title



# ---------------------
# PROJECT IMAGES
# ---------------------
class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project,
        related_name='images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='projects/')

    def __str__(self):
        return f"Image for {self.project.title}"


# ---------------------
# PROJECT REACTION
# ---------------------
class ProjectReaction(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]

    project = models.ForeignKey(
        Project,
        related_name='reactions',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=10, choices=REACTION_CHOICES)

    class Meta:
        unique_together = ('project', 'user')

    def __str__(self):
        return f"{self.user} - {self.project} ({self.reaction})"


# ---------------------
# ACTIVITY LOG
# ---------------------
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=30)
    message = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)


# ---------------------
# KK PROFILE (CONNECTED TO USER + RESIDENT)
# ---------------------
class KKProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="kk_profile"
    )

    resident = models.OneToOneField(
        Resident,
        on_delete=models.CASCADE,
        related_name="kk_profile"
    )

    SCHOOL_STATUS_CHOICES = [
        ('in_school', 'In School Youth'),
        ('out_school', 'Out of School Youth'),
    ]

    school_status = models.CharField(
        max_length=20,
        choices=SCHOOL_STATUS_CHOICES,
        default='in_school'
    )

    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def age(self):
        if self.resident and self.resident.birthday:
            today = date.today()
            return today.year - self.resident.birthday.year - (
                (today.month, today.day) <
                (self.resident.birthday.month, self.resident.birthday.day)
            )
        return None

    def __str__(self):
        return f"KK Profile - {self.user.username}"


# ---------------------
# SK MEMBER
# ---------------------
class SKMember(models.Model):
    ROLE_CHOICES = [
        ('chairman', 'SK Chairman'),
        ('secretary', 'SK Secretary'),
        ('treasurer', 'SK Treasurer'),
        ('appro', 'SK Kagawad – Appro'),
        ('education', 'SK Kagawad – Education'),
        ('health', 'SK Kagawad – Health'),
        ('sports', 'SK Kagawad – Sports'),
        ('social', 'SK Kagawad – Social Inclusion'),
        ('livelihood', 'SK Kagawad – Livelihood'),
        ('environment', 'SK Kagawad – Environment'),
    ]

    name = models.CharField(max_length=150)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    photo = models.ImageField(upload_to='sk_members/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']   # 👈 controls display order

    def __str__(self):
        return f"{self.get_role_display()} - {self.name}"


# ---------------------
# FEEDBACK & SUGGESTIONS
# ---------------------
class Suggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()

    STATUS_CHOICES = [
        ('new', 'New'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )

    is_important = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback from {self.user.username}"


# ---------------------
# ANNOUNCEMENT
# ---------------------
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title
