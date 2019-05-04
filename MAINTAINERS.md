# Maintaining Bowler

This documents the processes for maintaining Bowler.

## Reviewing Pull Requests

When developers submit pull requests, the following points should be considered
when deciding to accept, request changes, or reject them:

For new features:

* Is the feature appropriate for Bowler?
* Do we want to take responsibility for maintaining and fixing this feature?
* Is this implemented in a way that matches existing Bowler patterns and use cases?
* Is this a complete implementation, or is there a clear path to completion?
* Is the feature documented appropriately?

For all code changes:

* Does CI (test, lint, formatting) pass on all supported platforms?
* Does this include appropriate test case coverage?
* Is documentation updated as necessary?

When a PR has been accepted:

* Update PR title if necessary to clarify purpose.
* Prefer using merge commits from Github to record PR name and number.
* For automated PR's (like pyup.io), prefer using rebase from Github UI.

## Releasing New Versions

1. Decide on the next version number, based on what has been added to `master`
   since the previous release:

   * Major breaking changes should increment the first number and reset the other
     two, eg `0.10.0 -> 1.0.0`
   * New features should increment the second number and reset the third,
     eg `0.10.0 -> 0.11.0`
   * Bug fixes should only increment the third number, eg `0.10.0 -> 0.10.1`.

2. Update `bowler/__init__.py` with the new version number.

3. Update `CHANGELOG.md` with the new version, following the same pattern as
   previous versions.  Entries should reference both the PR number and any
   associated issue numbers related to the feature or change described.

   Contributers to this release should be acknowledged by including the output
   of `git shortlog -sn <previous tag>...`.

4. Commit the updated version number and changelog with a message following
   the pattern "(Feature | bugfix) release v<version>".

5. Push this commit to upstream master branch and wait for CI to run/pass.

6. Tag this commit with the version number (including the preceding "v")
   using `git tag -s v<version>`, and paste the contents of the changelog
   for this version as the tag's message.  Be sure to make a signed tag (`-s`)
   using a GPG key attached to your Github profile.

7. Push this tag to upstream using `git push --tags` and wait for CI to pass.

8. Publish this release to PyPI using `make release` to build and upload
   the source distribution and wheels.