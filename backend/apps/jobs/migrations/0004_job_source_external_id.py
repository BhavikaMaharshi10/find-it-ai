from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0003_alter_jobembedding_embedding_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="job",
            name="source",
            field=models.CharField(db_index=True, default="seed", max_length=50),
        ),
        migrations.AddField(
            model_name="job",
            name="external_id",
            field=models.CharField(blank=True, db_index=True, default="", max_length=255),
        ),
        migrations.AddConstraint(
            model_name="job",
            constraint=models.UniqueConstraint(
                condition=models.Q(("external_id__gt", "")),
                fields=("source", "external_id"),
                name="jobs_unique_source_external_id",
            ),
        ),
    ]
