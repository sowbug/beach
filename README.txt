Beach
=====

Written on August 27, 2011 in about six hours, including a lunch break. The
plan was for my kids and me to write a video game this summer, and we were
running out of time. So I looked out of our window for inspiration (we were
on vacation in Hawaii at the time).

Running the Game
----------------

On Windows or Mac OS X, locate the "run_game.pyw" file and double-click it.

Otherwise open a terminal / console and "cd" to the game directory and run:

  python run_game.py


How to Play the Game
--------------------

Use the mouse to move your character around. Gather stuff and put it in the
treasure chest. If the water touches you, your game is over.

- Things closer to the ocean tend to be worth more.

- Dropping off bigger batches of things awards more points.

- You can't run as fast when you're dragging a large batch of things.

Development notes 
-----------------

Creating a source distribution with::

   python setup.py sdist

You may also generate Windows executables and OS X applications::

   python setup.py py2exe
   python setup.py py2app

Upload files to PyWeek with::

   python pyweek_upload.py

Upload to the Python Package Index with::

   python setup.py register
   python setup.py sdist upload

