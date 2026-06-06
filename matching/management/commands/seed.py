from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from matching.models import Job, Application, Contract
from accounts.models import Profile
import random


class Command(BaseCommand):
    help = "seedデータ作成（マッチングアプリ用）"

    @transaction.atomic
    def handle(self, *args, **kwargs):

        # -------------------
        # 初期化（冪等性）
        # -------------------
        Contract.objects.all().delete()
        Application.objects.all().delete()
        Job.objects.all().delete()
        Profile.objects.filter(user__username__startswith="worker").delete()
        Profile.objects.filter(user__username__startswith="company").delete()
        User.objects.filter(username__startswith="worker").delete()
        User.objects.filter(username__startswith="company").delete()

        # -------------------
        # ユーザー作成
        # -------------------
        workers = []
        companies = []

        for i in range(5):
            user = User.objects.create_user(
            username=f"worker{i}",
            password="pass1234"
            )

            Profile.objects.create(
                user=user,
                role="worker",
                bio="テストワーカーです"
            )

            workers.append(user)

        for i in range(2):
            user = User.objects.create_user(
            username=f"company{i}",
            password="pass1234"
            )

            Profile.objects.create(
                user=user,
                role="company",
                bio="テスト企業です"
            )

            companies.append(user)
        
        # -------------------
        # 案件作成
        # -------------------
        jobs = []

        for c in companies:
            for i in range(3):
                job = Job.objects.create(
                    title=f"{c.username}案件{i}",
                    description="Webシステム開発案件（Django / API開発）",
                    reward=random.randint(5000, 20000),
                    max_workers=1,
                    client=c
                )
                jobs.append(job)

        # -------------------
        # 応募 → 採用ロジック
        # -------------------
        available_workers = workers.copy()
        random.shuffle(available_workers)

        applications = []

        for job in jobs:

            # 応募者がいない場合はスキップ
            if not available_workers:
                break

            worker = available_workers.pop()

            # 応募作成（まずはpending）
            app = Application.objects.create(
                job=job,
                user=worker,
                status="pending"
            )
            applications.append(app)

        # -------------------
        # 採用処理（選考）
        # -------------------
        for app in applications:

            job = app.job

            # max_workersチェック（超重要）
            current_contracts = Contract.objects.filter(job=job).count()
            if current_contracts >= job.max_workers:
                app.status = "rejected"
                app.save()
                continue

            # 採用
            app.status = "accepted"
            app.save()

            Contract.objects.create(
                job=job,
                worker=app.user,
                client=job.client,
                status="active"
            )

        self.stdout.write(self.style.SUCCESS("seed完了（マッチングフロー版）"))