using DayEye.DayEyeDb.Entities;
using DayEye.DayEyeDb.Mappings;
using System;
using System.Collections.Generic;
using System.Data.Entity;
using System.Linq;
using System.Web;

namespace DayEye.DayEyeDb
{
    public class DayEyeDbContext : DbContext
    {

        public DbSet<User> Users { get; set; }

        public DayEyeDbContext() : base("name=DayEye")
        {
            Configuration.LazyLoadingEnabled = false;
            Database.SetInitializer<DayEyeDbContext>(null);
        }

        protected override void OnModelCreating(DbModelBuilder modelBuilder)
        {

            modelBuilder.Configurations.Add(new UserMapping());

        }

    }
}