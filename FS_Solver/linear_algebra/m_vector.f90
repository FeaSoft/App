! Description:
! Definition of a vector.
module m_vector
    implicit none
    
    private
    public t_vector, new_vector
    
    type t_vector
        integer           :: n_vals ! number of values (size)
        real, allocatable :: at(:)  ! values
    contains
        final :: destructor
    end type
    
    interface new_vector
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Vector constructor.
    type(t_vector) function constructor(n_vals) result(this)
        integer, intent(in) :: n_vals ! number of values (size)
        this%n_vals = n_vals
        allocate(this%at(this%n_vals), source=0.0)
    end function
    
    ! Description:
    ! Vector destructor.
    subroutine destructor(this)
        type(t_vector), intent(inout) :: this
        if (allocated(this%at)) deallocate(this%at)
    end subroutine
    
end module
