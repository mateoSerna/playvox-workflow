db.createUser(
  {
    user: "playvox",
    pwd: "playvox",
    roles: [
      {
        role: "readWrite",
        db: "playvox"
      }
    ]
  }
);
