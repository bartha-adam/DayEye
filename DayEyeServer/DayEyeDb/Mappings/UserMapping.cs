using DayEye.DayEyeDb.Entities;
using System;
using System.Collections.Generic;
using System.Data.Entity.ModelConfiguration;
using System.Linq;
using System.Web;

namespace DayEye.DayEyeDb.Mappings
{
    public class UserMapping : EntityTypeConfiguration<User>
    {
        public UserMapping()
        {
            ToTable("Users", "dbo");
            HasKey(x => x.Email);
        }

    }
}