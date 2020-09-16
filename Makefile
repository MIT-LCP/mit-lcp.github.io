.PHONY: help run update sitedata-changed deploy-staging deploy-production \
github-update-dev github-update-staging github-update-production

TEMP_DEPLOY_BRANCH = "temp-deploy"

help:
	@echo '                                                                                   '
	@echo 'Recipes for the LCP website (http://lcp.mit.edu)                                   '
	@echo '                                                                                   '
	@echo 'Usage:                                                                             '
	@echo '   make run                      Run the website locally                           '
	@echo '   make update                   Load updates made to the sitedata folder          '
	@echo '                                                                                   '

run:
	(source activate; flask run)

update:
	# Update the publications
	./scripts/change.py
	# Determine if changes are detected in the sitedata folder
	make sitedata-changed
	# If changes are detected, commit changes on temp branch.
	make github-update-temp
	git checkout dev
	# Update the dev, staging, and production branches.
	make github-update-dev
	# make github-update-staging
	make github-update-production
	# Update the live websites
	make deploy-staging
	make deploy-production
	@echo '\n**************************'
	@echo ' All updates are complete!'
	@echo '**************************\n'

sitedata-changed:
	./scripts/sitedata-changed.sh

github-update-temp:
	@echo '\nMaking updates on a temporary branch.\n'
	-git branch -D $(TEMP_DEPLOY_BRANCH)
	git checkout -b $(TEMP_DEPLOY_BRANCH)
	git add sitedata/
	git commit -m "update sitedata with makefile."
	@echo '\nUpdates on temporary branch complete.\n'

github-update-dev:
	@echo '\nMaking updates on the dev branch.\n'
	git checkout dev
	git pull origin dev
	-git cherry-pick $(TEMP_DEPLOY_BRANCH)
	@echo '\nUpdates on the dev branch complete.\n'
	# git push dev
	@echo "Pushed to dev branch on GitHub."

github-update-staging:
	@echo '\nMaking updates on the staging branch.\n'
	git checkout staging
	git pull origin staging
	-git cherry-pick $(TEMP_DEPLOY_BRANCH)
	@echo '\nUpdates on the staging branch complete.\n'
	# git push staging
	@echo "Pushed to staging branch on GitHub."
	git checkout dev

github-update-production:
	@echo '\nMaking updates on the production branch.\n'
	git checkout production
	git pull origin production
	-git cherry-pick $(TEMP_DEPLOY_BRANCH)
	@echo '\nUpdates on the production branch complete.\n'
	# git push production
	@echo "Pushed to production branch on GitHub."
	git checkout dev

deploy-staging:
	@echo '\nChanges deployed to the staging website.\n'

deploy-production:
	@echo '\nChanges deployed to the production website.\n'
